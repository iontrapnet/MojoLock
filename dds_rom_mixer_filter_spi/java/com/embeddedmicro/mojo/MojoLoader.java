package com.embeddedmicro.mojo;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;
import java.util.Arrays;
import java.util.List;
import jssc.SerialPort;
import jssc.SerialPortException;
import jssc.SerialPortList;
import jssc.SerialPortTimeoutException;

public class MojoLoader
{
  private SerialPort serialPort;
  private boolean terminal;

  public MojoLoader()
  {
    this.terminal = false;
  }

  private void updateProgress(final float value) {
    //System.out.print("\r\033[20C" + 
    //  String.format("%-4s", new Object[] { (int)(value * 100.0F) + "%" }));
  }

  private void updateText(final String text)
  {
    //System.out.print("\n" + String.format("%-20s", new Object[] { text }));
  }

  public void restartMojo() throws InterruptedException, SerialPortException
  {
    this.serialPort.setDTR(false);
    Thread.sleep(5L);
    for (int i = 0; i < 5; i++) {
      this.serialPort.setDTR(false);
      Thread.sleep(5L);
      this.serialPort.setDTR(true);
      Thread.sleep(5L);
    }
  }

  public void clearFlash(final String port) {
    MojoLoader.this.updateText("Connecting...");
    if (!MojoLoader.this.terminal)
      MojoLoader.this.updateProgress(0.0F);
    try {
      MojoLoader.this.connect(port);
    } catch (Exception e) {
      MojoLoader.this.onError("Could not connect to port " + port + "!");
      return;
    }
    try
    {
      MojoLoader.this.restartMojo();
    } catch (InterruptedException|SerialPortException e) {
      MojoLoader.this.onError(e.getMessage());
      return;
    }
    try
    {
      MojoLoader.this.updateText("Erasing...");

      MojoLoader.this.serialPort.readBytes();

      MojoLoader.this.serialPort.writeByte((byte)69);

      if (MojoLoader.this.serialPort.readBytes(1, 10000)[0] != 68) {
        MojoLoader.this.onError("Mojo did not acknowledge flash erase!");
        return;
      }

      MojoLoader.this.updateText("Done");
      MojoLoader.this.updateProgress(1.0F);
    }
    catch (SerialPortException|SerialPortTimeoutException e) {
      MojoLoader.this.onError(e.getMessage());
      return;
    }
    try
    {
      MojoLoader.this.serialPort.closePort();
    } catch (SerialPortException e) {
      MojoLoader.this.onError(e.getMessage());
      return;
    }
  }

  public void sendBin(final String port, final String binFile, final boolean flash, final boolean verify)
  {
    MojoLoader.this.updateText("Connecting...");
    if (!MojoLoader.this.terminal)
      MojoLoader.this.updateProgress(0.0F);
    try {
      MojoLoader.this.connect(port);
    } catch (Exception e) {
      MojoLoader.this.onError("Could not connect to port " + port + "!");
      return;
    }

    File file = new File(binFile);
    InputStream bin = null;
    try {
      bin = new BufferedInputStream(new FileInputStream(file));
    } catch (FileNotFoundException e) {
      MojoLoader.this.onError("The bin file could not be opened!");
      return;
    }
    try
    {
      MojoLoader.this.restartMojo();
    } catch (InterruptedException|SerialPortException e) {
      MojoLoader.this.onError(e.getMessage());
      try {
        bin.close();
      } catch (IOException e1) {
        e1.printStackTrace();
      }
      return;
    }
    try
    {
      MojoLoader.this.serialPort.readBytes();

      if (flash)
        MojoLoader.this.updateText("Erasing flash...");
      else {
        MojoLoader.this.updateText("Loading to RAM...");
      }
      if (flash) {
        if (verify)
          MojoLoader.this.serialPort.writeByte((byte)86);
        else
          MojoLoader.this.serialPort.writeByte((byte)70);
      }
      else MojoLoader.this.serialPort.writeByte((byte)82);

      if (MojoLoader.this.serialPort.readBytes(1, 2000)[0] != 82) {
        MojoLoader.this.onError("Mojo did not respond! Make sure the port is correct.");
        bin.close();
        return;
      }

      int length = (int)file.length();

      byte[] buff = new byte[4];

      for (int i = 0; i < 4; i++) {
        buff[i] = ((byte)(length >> i * 8 & 0xFF));
      }

      MojoLoader.this.serialPort.writeBytes(buff);

      if (MojoLoader.this.serialPort.readBytes(1, 10000)[0] != 79) {
        MojoLoader.this.onError("Mojo did not acknowledge transfer size!");
        bin.close();
        return;
      }

      if (flash) {
        MojoLoader.this.updateText("Loading to flash...");
      }

      int count = 0;
      int oldCount = 0;
      int percent = length / 100;
      byte[] data = new byte[percent];
      while (true) {
        int avail = bin.available();
        avail = avail > percent ? percent : avail;
        if (avail == 0)
          break;
        int read = bin.read(data, 0, avail);
        MojoLoader.this.serialPort.writeBytes(Arrays.copyOf(data, read));
        count += read;

        if (count - oldCount > percent) {
          oldCount = count;
          float prog = count / length;
          MojoLoader.this.updateProgress(prog);
        }
      }

      MojoLoader.this.updateProgress(1.0F);

      if (MojoLoader.this.serialPort.readBytes(1, 2000)[0] != 68) {
        MojoLoader.this.onError("Mojo did not acknowledge the transfer!");
        bin.close();
        return;
      }

      bin.close();

      if ((flash) && (verify)) {
        MojoLoader.this.updateText("Verifying...");
        bin = new BufferedInputStream(new FileInputStream(file));
        MojoLoader.this.serialPort.writeByte((byte)83);

        int size = (int)(file.length() + 5L);
        int tmp;
        if (((tmp = MojoLoader.this.serialPort.readBytes(1, 2000)[0]) & 0xFF) != 170) {
          MojoLoader.this.onError("Flash does not contain valid start byte! Got: " + tmp);
          bin.close();
          return;
        }

        int flashSize = 0;
        for (int i = 0; i < 4; i++) {
          flashSize |= (MojoLoader.this.serialPort.readBytes(1, 2000)[0] & 0xFF) << i * 8;
        }

        if (flashSize != size) {
          MojoLoader.this.onError("File size mismatch!\nExpected " + size + " and got " + flashSize);
          bin.close();
          return;
        }

        count = 0;
        oldCount = 0;
        int num;
        while ((num = bin.read()) != -1)
        {
          int d = MojoLoader.this.serialPort.readBytes(1, 2000)[0] & 0xFF;
          if (d != num) {
            MojoLoader.this.onError("Verification failed at byte " + count + " out of " + length + "\nExpected " + num + " got " + d);
            bin.close();
            return;
          }
          count++;
          if (count - oldCount > percent) {
            oldCount = count;
            float prog = count / length;
            MojoLoader.this.updateProgress(prog);
          }
        }
        MojoLoader.this.updateProgress(1.0F);
      }

      if (flash) {
        MojoLoader.this.serialPort.writeByte((byte)76);
        if ((MojoLoader.this.serialPort.readBytes(1, 5000)[0] & 0xFF) != 68) {
          MojoLoader.this.onError("Could not load from flash!");
          bin.close();
          return;
        }
      }

      bin.close();
    } catch (IOException|SerialPortException|SerialPortTimeoutException e) {
      MojoLoader.this.onError(e.getMessage());
      return;
    }

    MojoLoader.this.updateText("Done");
    try
    {
      MojoLoader.this.serialPort.closePort();
    } catch (SerialPortException e) {
      MojoLoader.this.onError(e.getMessage());
      return;
    }
  }

  private void onError(String e) {
    if (e == null)
      e = "";
    updateProgress(0.0F);
    updateText("");

    if ((this.serialPort != null) && (this.serialPort.isOpened()))
      try {
        this.serialPort.closePort();
      } catch (SerialPortException e1) {
        e1.printStackTrace();
      }
  }

  public void connect(String portName) throws Exception {
    if (portName.equals(""))
      throw new Exception("A serial port must be selected!");
    if (!Arrays.asList(SerialPortList.getPortNames()).contains(portName)) {
      throw new Exception("Port " + portName + " could not be found. Please select a different port.");
    }

    this.serialPort = new SerialPort(portName);
    this.serialPort.openPort();
    this.serialPort.setParams(115200, 8, 1, 0);
  }
}