module simple_iir (clk, rst, once, done, coef, x, yout);
parameter	DATAWIDTH = 16;
parameter	COEFWIDTH = 16;
input clk, rst, once;
output reg done;
input [$clog2(COEFWIDTH)-1:0] coef;
input [DATAWIDTH-1:0] x;
output [DATAWIDTH-1:0] yout;

reg state;
reg [DATAWIDTH+COEFWIDTH-1:0] y;

wire [COEFWIDTH-1:0] minusone;
assign minusone = -1;

wire [DATAWIDTH-1:0] yout;
assign yout = y[DATAWIDTH+COEFWIDTH-1:COEFWIDTH];

reg [DATAWIDTH-1:0] xmyout;

always @ (posedge clk)
if (rst) begin
  y <= 0;
  state <= 0;
end else begin
  done <= 1'b0;
  if (coef == 0) begin
    y <= 0;
  end
  case (state)
    1'd0: begin
        if (once) begin
          xmyout <= x - yout;
          state <= 1'd1;
        end
    end
    1'd1: begin
        y <= y + (xmyout[DATAWIDTH-1] ? -(~{minusone,xmyout}+1)<<coef : xmyout<<coef);
        done <= 1'b1;
        state <= 1'd0;
    end
  endcase
end

endmodule