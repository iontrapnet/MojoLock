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
def divider_test(dut):
    """Try accessing the design."""
    #inputfile=csv.reader(open('input.csv','r'))
    #input = []
    #for row in inputfile:
    #    input.append(0 if len(row) == 0 else int(row[0]))
    clk_thread = cocotb.fork(Clock(dut.clk, 2).start())
    
    yield reset_dut(dut.rst, 10)
    dut._log.info("After reset")
    
    dut._log.info("Running test!")
    dut.shift <= 1
    a = -int(65536*0.1)
    if a < 0: a += 65536
    b = int(65536*0.6)
    dut._log.info('a = ' + str(a) + ',b=' + str(b)) 
    dut.in0 <= a
    dut.in1 <= b
    dut.once <= 1
    yield Timer(2)
    dut.once <= 0
    i = 1
    while dut.done == 0:
        dut._log.info('i = ' + str(i))
        i += 1
        yield Timer(2)
    yield Timer(2)
    out = dut.out.value.integer
    if out > 32767: out -= 65536
    dut._log.info('out = ' + str(out) + ',' + str(out/65536.))
    #output = []
    #for cycle in range(len(input)):
    #    yield Timer(4)
    #    dut.x <= input[cycle]
    #    dut.start <= 1
    #    yield Timer(2)
    #    dut.start <= 0
    #    while dut.finish == 0:
    #        yield Timer(2)
    #    output.append(dut.yout.value.integer)
    dut._log.info("Running test!")
    #yield clk_thread.join()
    #outputfile = csv.writer(open('output.csv', 'wb'))
    #for i in output:
    #    outputfile.writerow([str(i if i < 0x80000000 else i-0x100000000)])