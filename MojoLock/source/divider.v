module divider (clk,rst,once,done,in0,in1,out,shift); 
    input         clk, rst;                           // clock and reset
    input         once;                               // start
    output reg    done;                               // ready
    input  [15:0] in0;                                  
    input  [15:0] in1;                                 
    output [15:0] out;
    input  [3:0]  shift;                                 
    reg    [2:0]  count;
    reg           s;
      
    /*reg    [15:0] q;
    reg    [15:0] d;
    reg    [15:0] r;
    wire   [16:0] sub = {r[14:0],q[15]}-d;
    assign        out = q;*/
    
    /*reg    [63:0] xi;
    reg    [63:0] yi;
    reg    [31:0] xy;   
    reg    [31:0] two_minus_yi;
    wire   [63:0] mul;
    assign mul  = xy * two_minus_yi;    
    assign out  = xi[62:47] + |xi[46:44];*/

    reg [15:0] xi;
    reg [17:0] b18;
    reg [35:0] x36;
    wire [35:0] mul;
    assign mul = x36[34:17] * b18;
    assign out = b18[15:0];
    always @ (posedge clk or posedge rst) begin
        if (rst) begin
            count <= 0;
            done <= 0; 
        end else begin
            done <= 0;
            if (count == 0) begin 
              if (once) begin
                  /*q <= in0 << shift;//0;//in0;
                  d <= in1;
                  r <= in0 >> shift;//in0;//0;*/
                  
                  /*xi[62:31] <= {1'b0,in0,15'b0};
                  xy <= {1'b0,in1,15'b0};
                  two_minus_yi <= {1'b1,~in1,15'b1} + 1'b1;*/
                  
                  if (shift == 4'h0) begin
                    s <= 0;
                    b18 <= {in0[15],in0[15],in0};
                    count <= 0;
                    done <= 1;
                  end else if (shift == 4'hF) begin
                    s <= 0;
                    b18 <= {2'b0,in1};
                    count <= 0;
                    done <= 1;
                  end else begin
                    s <= in0[15];
                    xi <= in0 << (shift - 1);
                    b18 <= {2'b0,in1 << (shift - 1)};
                    x36 <= 0;
                    count <= 1;
                  end
                  
              end
            end else begin
                /*if (sub[16]) begin
                  r <= {r[14:0],q[15]};
                  q <= {q[14:0],1'b0};
                end else begin
                  r <= sub[15:0];
                  q <= {q[14:0],1'b1};
                end
                if (count == 5'h10) begin*/
                
                /*if (count[0]) begin
                  yi <= mul;
                  xy <= xi[62:31];
                end else begin
                  xi <= mul; 
                  xy <= yi[62:31];     
                  two_minus_yi <= ~yi[62:31] + 1'b1;
                end               
                if (count == 4'd8) begin*/
                
                case (count)
                3'd1: x36[34:17] <= {2'b1,rom(b18[14:11]),8'b0};
                3'd2: b18 <= ~mul[32:15] + 1'b1;
                3'd3: begin x36 <= mul; b18 <= {2'b0,s?~xi+1'b1:xi}; end
                3'd4: x36 <= mul;
                3'd5: b18[15:0] <= x36[31:16] + |x36[15:13];
                3'd6: b18[15:0] <= s ? (~b18[15:0] + 1'b1) : b18[15:0];
                endcase
                if (count == 3'd6) begin

                    count <= 0;
                    done <= 1;        
                end else begin
                    count <= count + 1; 
                end
            end
        end 
    end
    function [7:0] rom;
    input [3:0] b;
    case (b)
    4'h0: rom = 8'hff; 4'h1: rom = 8'hdf;
    4'h2: rom = 8'hc3; 4'h3: rom = 8'haa;
    4'h4: rom = 8'h93; 4'h5: rom = 8'h7f;
    4'h6: rom = 8'h6d; 4'h7: rom = 8'h5c;
    4'h8: rom = 8'h4d; 4'h9: rom = 8'h3f;
    4'ha: rom = 8'h33; 4'hb: rom = 8'h27;
    4'hc: rom = 8'h1c; 4'hd: rom = 8'h12;
    4'he: rom = 8'h08; 4'hf: rom = 8'h00;
    endcase
    endfunction
endmodule