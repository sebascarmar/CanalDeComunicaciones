
//! @title polyphase_filtro_fir - Testbench

`timescale 1ns/1ps

module tb_polyphase_filtro_fir ();

  parameter NB_INPUT   = 8; //! NB of input
  parameter NBF_INPUT  = 7; //! NBF of input
  parameter NB_OUTPUT  = 8; //! NB of output
  parameter NBF_OUTPUT = 7; //! NBF of output
  parameter NB_COEFF   = 8; //! NB of Coefficients
  parameter NBF_COEFF  = 7; //! NBF of Coefficients
  parameter N_BAUD     = 6; //! N OF BAUDIOS
  parameter N_OS       = 4; //! OVERSAMPLING
  parameter NB_PHASE   = 2; 
 
  reg                         tb_clk = 1'b1              ;
  reg                         tb_en                      ;
  reg                         tb_srst                    ;
  reg         [NB_INPUT -1:0] tb_is_data                 ;
  reg  signed [NB_COEFF -1:0] coeff    [N_BAUD*N_OS-1:0] ;

  wire        [NB_OUTPUT-1:0] tb_os_data                 ;

  reg                         aux_tb_en                  ;
  reg                         aux_tb_srst                ;
  reg         [NB_INPUT -1:0] aux_tb_is_data             ;

  wire        [NB_PHASE -1:0] control                    ;

  always @(posedge tb_clk) begin
    coeff[0 ] <= 8'b0000_0000;
    coeff[1 ] <= 8'b0000_0000;
    coeff[2 ] <= 8'b0000_0000;
    coeff[3 ] <= 8'b0000_0000;
    coeff[4 ] <= 8'b1111_1111;
    coeff[5 ] <= 8'b1110_1100;
    coeff[6 ] <= 8'b1111_1100;
    coeff[7 ] <= 8'b1111_1100;
    coeff[8 ] <= 8'b0000_0000;
    coeff[9 ] <= 8'b0101_0000;
    coeff[10] <= 8'b0001_0011;
    coeff[11] <= 8'b0001_1100;
    coeff[12] <= 8'b0010_0000;
    coeff[13] <= 8'b0001_1100;
    coeff[14] <= 8'b0001_0011;
    coeff[15] <= 8'b0101_0000;
    coeff[16] <= 8'b1111_1111;
    coeff[17] <= 8'b1111_1100;
    coeff[18] <= 8'b1111_1100;
    coeff[19] <= 8'b1110_1100;
    coeff[20] <= 8'b0000_0000;
    coeff[21] <= 8'b0000_0000;
    coeff[22] <= 8'b0000_0000;
    coeff[23] <= 8'b0000_0000;
  end

  //! Clock  //Periodo de 40ns
  always #20 tb_clk = ~tb_clk;

  always @(posedge tb_clk) begin
    tb_en      <= aux_tb_en      ;
    tb_srst    <= aux_tb_srst    ;
    tb_is_data <= aux_tb_is_data ;
  end

  //! Instance CONTROL
  control 
  #(
    .NB_PHASES(NB_PHASE) 
  )
  u_control
  (
    .i_reset    (tb_srst) ,
    .i_clock    (tb_clk ) ,
    .o_control  (control)
  );

  //! Instance of FIR
  polyphase_filtro_fir
    #(
      .NB_INPUT   (NB_INPUT  ),  //! NB of input
      .NBF_INPUT  (NBF_INPUT ),  //! NBF of input
      .NB_OUTPUT  (NB_OUTPUT ),  //! NB of output
      .NBF_OUTPUT (NBF_OUTPUT),  //! NBF of output
      .NB_COEFF   (NB_COEFF  ),  //! NB of Coefficients
      .NBF_COEFF  (NBF_COEFF ),  //! NBF of Coefficients
      .N_BAUD     (N_BAUD    ),
      .N_OS       (N_OS      ),
      .NB_PHASE   (NB_PHASE  )
    )
    u_polyphase_filtro_fir 
      (
        .o_os_data  (tb_os_data),
        .i_is_data  (tb_is_data),
        .i_coeff    (coeff     ),
        .i_control  (control   ),
        .i_en       (tb_en     ),
        .i_srst     (tb_srst   ),
        .clk        (tb_clk    )
      );

  // Stimulus
  real i;
  real aux;
  initial begin
    $display("");
    $display("Simulation Started");
    //$dumpfile("./verification/tb_filtro_fir/waves.vcd");
    //$dumpvars(0, tb_filtro_fir);
    #5
    aux_tb_en         = 1'b1;
    aux_tb_srst       = 1'b1;
    #40 @(posedge tb_clk);  //! Alineacion con el flanco de ciclo de reloj
    aux_tb_en         = 1'b1;
    aux_tb_srst       = 1'b0;
    #1000 @(posedge tb_clk);  //! Alineacion con el flanco de ciclo de reloj
    //! Se modela el comportamiento de una senoidal de 1khz, muestreada con una de 25khz
    for (i=0;i<4000;i=i+1) begin
      aux = $sin(2.0*3.1415926*i/25000.0*1000.0)*(2**NBF_INPUT); // se multiplica por (2**NBF_INPUT) para que funciona como un adc y la lectura este correctamente cuantizada. Esto es asi porque se desea desplazar la parte fraccional a la parte entera.
       if(aux > 127.0)
	        aux_tb_is_data = 8'h7F;
       else
	        aux_tb_is_data = aux;
      #40               //! El tiempo de retardo en cada iteracion for, equivale a una muestra por periodo de reloj. Si fuera 20 serian 2 muestras
      @(posedge tb_clk);  //! Alineacion con el flanco de ciclo de reloj
    end
    $display("Simulation Finished");
    $display("");
    $finish;
  end

endmodule
