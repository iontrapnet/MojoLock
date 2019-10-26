module filter (
    input clk,  // clock
    input rst,  // reset
    input once,
    output done,
    input [15:0] in,
    output [15:0] out,
    input [3:0] a1,
    input [3:0] a2
  );

wire done1;
wire [15:0] y1;
simple_iir #(.DATAWIDTH(16), .COEFWIDTH(16)) iir1(.clk(clk), .rst(rst), .once(once), .done(done1), .coef(a1), .x(in), .yout(y1));
simple_iir #(.DATAWIDTH(16), .COEFWIDTH(16)) iir2(.clk(clk), .rst(rst), .once(done1), .done(done), .coef(a2), .x(y1), .yout(out));

//butterworth #(.DATAWIDTH(32), .COEFWIDTH(32), .COEFPOINT(24)) butterworth(.clk(clk), .reset(rst), .a1(a1), .a2(a2), .b0(c0), .b1(c1), .b2(c2), .x(x), .yout(yout));

endmodule
