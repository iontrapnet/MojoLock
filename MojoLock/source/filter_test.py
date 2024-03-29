import cocotb
from cocotb.clock import Clock
from cocotb.decorators import coroutine
from cocotb.triggers import Timer
import csv
    
@cocotb.coroutine
def reset_dut(reset_p, duration):
    reset_p <= 1
    yield Timer(duration)
    reset_p <= 0
    
@cocotb.test()
def filter_test(dut):
    """Try accessing the design."""
    inputfile=csv.reader(open('input.csv','r'))
    input = []
    for row in inputfile:
        input.append(0 if len(row) == 0 else int(row[0]))
    clk_thread = cocotb.fork(Clock(dut.clk, 2).start())
    
    coef = 11
    dut.a1 <= coef
    dut.a2 <= coef
    dut.in0 <= 0
    yield reset_dut(dut.rst, 10)
    dut._log.info("After reset")
    
    dut._log.info("Running test!")
    output = []
    for cycle in range(len(input)):
        yield Timer(4)
        dut.in0 <= input[cycle]
        dut.once <= 1
        yield Timer(2)
        dut.once <= 0
        while dut.done == 0:
            yield Timer(2)
        output.append(dut.out.value.integer)
    dut._log.info("Running test!")
    #yield clk_thread.join()
    outputfile = csv.writer(open('output.csv', 'wb'))
    for i in output:
        outputfile.writerow([str(i if i < 0x80000000 else i-0x100000000)])