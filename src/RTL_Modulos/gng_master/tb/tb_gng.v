//------------------------------------------------------------------------------
//
// tb_gng.sv
//
// This file is part of the Gaussian Noise Generator IP Core
//
// Description
//     Verilog testbench for module gng. Generate noise sequences of
// length N. 
//
//------------------------------------------------------------------------------

`timescale 1 ns / 1 ps

module tb_gng;

// Parameters
parameter ClkPeriod = 10.0;
parameter Dly = 1.0;
parameter N = 1000000;


// Local variables
reg clk;
reg rstn;
reg ce;

wire valid_out;
wire [15:0] data_out;


// Instances
gng #(
   .INIT_Z1(64'd5030521883283424767),
   .INIT_Z2(64'd18445829279364155008),
   .INIT_Z3(64'd18436106298727503359)
)
u_gng 
(
    // System signals
    .clk (clk ),                    // system clock
    .rstn(rstn),                   // system synchronous reset, active low

    // Data interface
    .ce       (ce       ),                     // clock enable
    .valid_out(valid_out),             // output data valid
    .data_out (data_out )       // output data, s<16,11>
);

// System signals
initial begin
    clk <= 1'b0;
    forever #(ClkPeriod/2) clk = ~clk;
end

initial begin
    rstn <= 1'b0;
    #(ClkPeriod*2) rstn = 1'b1;
end


// Main process

initial begin
    ce = 0;

    #(ClkPeriod*10)
    repeat (N) begin
        @(posedge clk);
        #(Dly);
        ce = 1;
    end
    @(posedge clk);
    #(Dly);
    ce = 0;

    #(ClkPeriod*20)
    $stop;
end

endmodule
