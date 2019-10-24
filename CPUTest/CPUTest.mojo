<?xml version="1.0" encoding="UTF-8"?>
<project name="CPUTest" board="Mojo V3" language="Lucid">
  <files>
    <src top="true">mojo_top.luc</src>
    <src>instRom.luc</src>
    <ucf lib="true">mojo.ucf</ucf>
    <ucf>spi.ucf</ucf>
    <component>cclk_detector.luc</component>
    <component>uart_rx.luc</component>
    <component>simple_ram.v</component>
    <component>reg_interface.luc</component>
    <component>spi_slave.luc</component>
    <component>avr_interface.luc</component>
    <component>uart_tx.luc</component>
    <component>reset_conditioner.luc</component>
  </files>
</project>
