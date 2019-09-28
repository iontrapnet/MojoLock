<?xml version="1.0" encoding="UTF-8"?>
<project name="MojoLock" board="Mojo V3" language="Lucid">
  <files>
    <src>simple_iir.v</src>
    <src>dds.luc</src>
    <src>spi.luc</src>
    <src>lia.luc</src>
    <src>adc.luc</src>
    <src top="true">mojo_top.luc</src>
    <src>pid.luc</src>
    <src>dac.luc</src>
    <src>filter.v</src>
    <src>rom.luc</src>
    <ucf>spi.ucf</ucf>
    <ucf lib="true">mojo.ucf</ucf>
    <component>reg_interface.luc</component>
    <component>spi_slave.luc</component>
    <component>uart_rx.luc</component>
    <component>simple_ram.v</component>
    <component>cclk_detector.luc</component>
    <component>reset_conditioner.luc</component>
    <component>avr_interface.luc</component>
    <component>uart_tx.luc</component>
    <core name="coregen_clk">
      <src>coregen_clk.v</src>
    </core>
  </files>
</project>
