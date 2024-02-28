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


// inputs
reg clock;
reg reset;
reg clock_enable;
reg [ 3:0] shifter_divider;

// outputs
wire valid_out;
wire [15:0] data_out;


// Instances
gng_top #(
   .INIT_Z1(64'd5030521883283424767),
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
    .i_shifter_divider (shifter_divider),

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
integer f; 

parameter SHIFTER_DIVIDER = 8;  // no superar 15
reg signed [15-SHIFTER_DIVIDER:0] data_signed;

initial begin
    
    shifter_divider = 0;
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

    //! TC002: SHIFTER INCREMENT       
  
    $display("##########################################################################");
    $display("#####################-TC002: SHIFTER INCREMENT ###########################");
    $display("##########################################################################");


    for(i=0; i<16; i=i+1) begin
        shifter_divider = i;
        #(ClkPeriod*20);
    end

    //!############################################################

    //! TC003: OBTENER DATA PARA LOG       
  
    $display("##########################################################################");
    $display("###################-TC003: OBTENER DATA PARA LOG #########################");
    $display("##########################################################################");

    shifter_divider = SHIFTER_DIVIDER;   //! CONFIGURE EL VALOR DEL PARAMETRO DIVIDER QUE DESEE LOGEAR

    f = $fopen("D:/run/gng_test/datos.txt", "w"); //! Abrir archivo para escritura, CONFIGURE EL PATH DE DESTINO
  
    $fwrite(f, "%d\n", shifter_divider); // Escribir dato en archivo
    repeat (5000) begin   //! escriba la cantidad de datos que desee obtener
      @(posedge clock) 
      if (valid_out) begin
        data_signed = data_out[15-SHIFTER_DIVIDER:0];
        $display("data_out(decimal) = %d, data_signed(decimal) = %d, data_signed(binary) = %b", data_out, data_signed, data_signed);
        $fwrite(f, "%d\n", data_signed); // Escribir dato en archivo
      end
    end
    
    $fclose(f); // Cerrar archivo cuando termina
    //!############################################################

    #(ClkPeriod*10);

    $finish;
end

endmodule
