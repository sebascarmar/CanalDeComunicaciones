`timescale 1ns / 100ps

module tb_single_port_ram();

  // Parametros 
  parameter RAM_WIDTH = 8;
  parameter RAM_DEPTH = 16;
  parameter LOGB2_RAM_DEPTH = $clog2(RAM_DEPTH-1); 

  //inputs
  reg [LOGB2_RAM_DEPTH-1:0] address_bus;
  reg [RAM_WIDTH-1:0] data_input;
  reg clock;
  reg write_enable;
  reg enable; 
  reg reset;
  reg register_enable;
  //outputs
  wire [RAM_WIDTH-1:0] data_output;

  // Instanciar UUT
  xilinx_single_port_ram_no_change
   #(
    .RAM_WIDTH(RAM_WIDTH),             // Specify RAM data width
    .RAM_DEPTH(RAM_DEPTH)              // Specify RAM depth (number of entries)
  ) 
  dut 
  (
    //input
    .address_bus(address_bus),         // address_bus, width determined from RAM_DEPTH
    .data_input(data_input),           // RAM data_input, width determined from RAM_WIDTH
    .clock(clock),                     // clock
    .write_enable(write_enable),       // write_enable 
    .enable(enable),                   // RAM enable, for additional power savings  //! 1'b1
    .reset(reset),                     // Output reset (does not affect memory contents)
    .register_enable(register_enable), // Output register_enable //! 1'b1
    // output
    .data_output(data_output)          // RAM data_output, width determined from RAM_WIDTH
  );

  // Generacion reloj
  always #5 clock = ~clock;
  
  // Proceso de escritura
  integer i;
  integer j; 

  initial begin
    clock = 0;
    reset = 0;
    enable = 1;
    write_enable = 1;
    register_enable = 0;
//!############################################################
    #100;
    @(posedge clock); 
    //! TC001: Proceso de escritura y lectura estandar

    $display("##########################################################################");
    $display("#############-TC001: Proceso de escritura y lectura estandar-#############");
    $display("##########################################################################");
    // Escritura valores incrementales
    for(i=0; i<RAM_DEPTH; i=i+1) begin
      address_bus = i; 
      data_input  = i; 
      #50; 
    end

    #100;
    @(posedge clock); 

    // Proceso de lectura con register_enable = 0
    write_enable = 0;
    #5;
    for(j=0; j<RAM_DEPTH; j=j+1) begin
      address_bus = j;
      #50;
      $display("Leido de address_bus register_enable=0 %d: %d", address_bus, data_output); 
    end // se lee todo en cero

    #100;
    @(posedge clock); 

    // Proceso de lectura con register_enable = 1
    register_enable = 1;
    #5;
    for(j=0; j<RAM_DEPTH; j=j+1) begin
      address_bus = j;
      #50;
      $display("Leido de address_bus register_enable=1 %d: %d", address_bus, data_output); 
    end // se habilita la lectura

//!############################################################
    #100;
    @(posedge clock); 
    //! TC002: Reset
    $display("##########################################################################");
    $display("##############################-TC002: Reset-##############################");
    $display("##########################################################################");

    #100;
    @(posedge clock); 

    reset = 1;
    #20;
    reset = 0;

    // Proceso de lectura
    write_enable = 0;
    for(j=0; j<RAM_DEPTH; j=j+1) begin
      address_bus = j;
      #50;
      $display("Leido de address_bus %d: %d", address_bus, data_output);  
    end  // se continua leyendo lo anterior, el reset no afecta el contenido de la memoria

//!############################################################
    #100;
    @(posedge clock); 
    //! TC003: Enable test

    $display("##########################################################################");
    $display("###########################-TC003: Enable Test-###########################");
    $display("##########################################################################");

    write_enable = 1;
    // Escritura valores incrementales por 2
    for(i=0; i<RAM_DEPTH; i=i+1) begin
      address_bus = i; 
      data_input  = 2*i; 
      #50; 
    end

    #100;
    @(posedge clock); 

    enable = 0;
    write_enable = 0;
    // Proceso de lectura enable = 0;
    for(j=0; j<RAM_DEPTH; j=j+1) begin
      address_bus = j;
      #50;
      $display("Leido de address_bus enable=0 %d: %d", address_bus, data_output); 
    end  // el chip queda a la salida con el valor antes de poner enable = 0

    write_enable = 1;
    // Escritura valores incrementales por 4
    for(i=0; i<RAM_DEPTH; i=i+1) begin
      address_bus = i; 
      data_input  = 4*i; 
      #50; 
    end //no escribe por estar enable = 0;

    #100;
    @(posedge clock); 

    enable = 1;
    write_enable = 0;
    // Proceso de lectura enable = 1;
    for(j=0; j<RAM_DEPTH; j=j+1) begin
      address_bus = j;
      #50;
      $display("Leido de address_bus enable=1 %d: %d", address_bus, data_output);  
    end  // los datos no se modificaron en la ultima escritura

//!############################################################

    $finish;
  end
      
  
endmodule