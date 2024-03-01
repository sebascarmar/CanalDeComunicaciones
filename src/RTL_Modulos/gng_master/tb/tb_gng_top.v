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

module tb_gng_top;

// Parameters
parameter ClkPeriod = 10.0;
parameter Dly = 1.0;
parameter N = 1000000;
parameter NB_DATA   = 16;

// inputs
reg clock;
reg reset;
reg clock_enable;
reg signed [NB_DATA-1:0] sigma_multiplier;

// outputs
wire valid_out;
wire signed [2*NB_DATA-1:0] data_out;


// Instances
gng_top #(
   .NB_DATA(NB_DATA                 ),
   .INIT_Z1(64'd5030521883283424767 ),
   .INIT_Z2(64'd18445829279364155008),
   .INIT_Z3(64'd18436106298727503359)
)
u_gng_top 
(
    // outputs
    .o_data (data_out ),       // output data, s<16,11>
    .o_valid(valid_out),      // output data valid

    // inputs
    .i_clock_enable(clock_enable  ),      // clock enable
    .i_sigma_multiplier (sigma_multiplier),

    // System signals
    .i_clock (clock ),                 // system clock
    .i_reset(reset)                // system synchronous reset, active low
);


// System signals
initial begin
    clock <= 1'b0;
    forever #(ClkPeriod/2) clock = ~clock;
end

initial begin
    reset <= 1'b1;
    #(ClkPeriod*2) reset = 1'b0;
end


// Main process

integer i;
integer k;
integer f; 

localparam MULTIPLIER = 0.1 ;    // MULTIPLICADOR -16 - 15
localparam SIGMA      = MULTIPLIER * 2048;    // formato S(16,11), 2048 = 2^11, equivale a 1

initial begin
    
    sigma_multiplier = 2048; // 2048 = 2^11, equivale a 1
    #(ClkPeriod*20);
//!############################################################
    //! TC000: CLOCK_ENABLE=0        
  
    $display("##########################################################################");
    $display("#####################-TC000: CLOCK_ENABLE = 0 ############################");
    $display("##########################################################################");

    clock_enable = 0;

    #(ClkPeriod*20);

//!############################################################

    //! TC001: CLOCK_ENABLE=1        
  
    $display("##########################################################################");
    $display("#####################-TC001: CLOCK_ENABLE = 1 ############################");
    $display("##########################################################################");

    clock_enable = 1;

    #(ClkPeriod*20);

//!############################################################

    //! TC002: INCREMENT       
  
    $display("##########################################################################");
    $display("#########################-TC002: INCREMENT ###############################");
    $display("##########################################################################");


    for(i=2048; i<=4096; i=i+1) begin  // de 1 a 2
        sigma_multiplier = i ;
        for(k=0; k<10; k=k+1) begin
            #(ClkPeriod);
            //$display("data = %b, sigma_multiplier = %d, mult = %b", u_gng_top.data, sigma_multiplier, data_out);
        end
        
    end

    //!############################################################

    //! TC003: OBTENER DATA PARA LOG       
  
    $display("##########################################################################");
    $display("###################-TC003: OBTENER DATA PARA LOG #########################");
    $display("##########################################################################");
    
    sigma_multiplier = SIGMA;   //! CONFIGURE EL VALOR DEL PARAMETRO MULTIPLIER QUE DESEE LOGEAR
    
    f = $fopen("D:/run/gng_test/datos.txt", "w"); //! Abrir archivo para escritura, CONFIGURE EL PATH DE DESTINO
    
    $fwrite(f, "%d\n", sigma_multiplier); // Escribir dato en archivo
    repeat (5000) begin   //! escriba la cantidad de datos que desee obtener
      @(posedge clock) 
      if (valid_out) begin
        $display("data = %d, data_out(decimal) = %d, data_out(binary) = %b", u_gng_top.data, data_out, data_out);
        $fwrite(f, "%d\n", data_out); // Escribir dato en archivo
      end
    end
        
    $fclose(f); // Cerrar archivo cuando termina
    //!############################################################

    #(ClkPeriod*10);

    $finish;
end

endmodule
