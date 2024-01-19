//! @title polyphase_filtro_fir


module polyphase_filtro_fir
#(
  parameter NB_INPUT   = 8, //! NB of input
  parameter NBF_INPUT  = 7, //! NBF of input
  parameter NB_OUTPUT  = 8, //! NB of output
  parameter NBF_OUTPUT = 7, //! NBF of output
  parameter NB_COEFF   = 8, //! NB of Coefficients
  parameter NBF_COEFF  = 7, //! NBF of Coefficients
  parameter N_BAUD     = 6, //! N OF BAUDIOS
  parameter N_OS       = 4, //! OVERSAMPLING
  parameter NB_PHASE   = 2
) 
(
  wire output signed [NB_OUTPUT-1:0] o_os_data                   , //! Output Sample
  wire input                         i_is_data                   , //! Input Sample
  wire input  signed [NB_COEFF -1:0] i_coeff   [N_BAUD*N_OS-1:0] , //! Input Sample
  wire input         [NB_PHASE -1:0] i_control                   , //! control
  wire input                         i_en                        , //! Enable
  wire input                         i_srst                      , //! Reset
  wire input                         clk                           //! Clock
);

//!*********************************************************************************/
//!*                                   LOCALPARAMETERS                             */
//!*********************************************************************************/
localparam NB_ADD     = NB_COEFF  + NB_INPUT + 2 ;
localparam NBF_ADD    = NBF_COEFF + NBF_INPUT    ;
localparam NBI_ADD    = NB_ADD    - NBF_ADD      ;
localparam NBI_OUTPUT = NB_OUTPUT - NBF_OUTPUT   ;
localparam NB_SAT     = NBI_ADD   - NBI_OUTPUT   ;

/*********************************************************************************/
/*                                   SHIFT_REGISTERS_FOR_DATA                    */
/*********************************************************************************/
// Variables
integer ptr1                    ;
integer ptr2                    ;
reg shift_register [N_BAUD-1:1] ; // Matrix for registers

// ShiftRegister model
always @(posedge clk) begin
  if (i_srst == 1'b1) begin
    for( ptr1 = 1 ; ptr1 < N_BAUD ; ptr1 = ptr1 + 1 ) begin: init
      shift_register[ptr1] <= {NB_INPUT{1'b0}};
    end
  end 
  else begin
    if ( ( i_en == 1'b1 ) && ( i_control == 2'b11 ) ) begin       //! CONTROL THRESHOLD VALUE CAN BE CHANGED FOR CONVENIENCE
      for( ptr2 = 1 ; ptr2 < N_BAUD ; ptr2 = ptr2 + 1 ) begin: shift_register_move
        if(ptr2==1) begin
          shift_register[ptr2] <= i_is_data;
        end
        else begin
          shift_register[ptr2] <= shift_register[ptr2-1];
        end
       end   
    end
  end
end
/*********************************************************************************/
/*                                   PARTIAL_PRODUCTS                            */
/*********************************************************************************/
// Variables
wire signed [NB_COEFF         -1:0] coeff_muxed [N_BAUD-1:0];  //6 mux, a cada uno se le asigna 4 coeficientes 
wire signed [NB_INPUT+NB_COEFF-1:0] products    [N_BAUD-1:0];  // Partial Products

// Generate partial products and mux structure
generate  
  genvar ptr;
  for( ptr = 0 ; ptr < N_BAUD ; ptr = ptr + 1 ) begin: multiply
    
    assign coeff_muxed[ptr] = ( i_control == 2'b00 ) ? i_coeff[N_OS*ptr] : { ( i_control == 2'b01 ) ? i_coeff[N_OS*ptr+1] : { ( i_control == 2'b10 ) ? i_coeff[N_OS*ptr+2] : i_coeff[N_OS*ptr+3] } } ;

    if (ptr==0) begin
      assign products[ptr] = ( i_is_data           ) ? coeff_muxed[ptr] :  ( - coeff_muxed[ptr] ) ;
    end
    else begin
      assign products[ptr] = ( shift_register[ptr] ) ? coeff_muxed[ptr] :  ( - coeff_muxed[ptr] ) ;
    end
  end
endgenerate

/*********************************************************************************/
/*                                   ADDITION                                    */
/*********************************************************************************/
// Variables
integer ptr3                      ;
reg signed [ NB_ADD - 1 : 0 ] sum ;

// Accumulator
always @( * ) begin: accum
  sum = { NB_ADD { 1'b0 } } ;
  for( ptr3 = 0 ; ptr3 < N_BAUD ; ptr3 = ptr3 + 1 ) begin: accumulator
    sum = sum + products[ptr3];
  end
end

/*********************************************************************************/
/*                                   OUTPUT_ASSIGNMENT                           */
/*********************************************************************************/

assign o_os_data = ( ~|sum[NB_ADD-1 -: NB_SAT+1] || &sum[NB_ADD-1 -: NB_SAT+1]) ? sum[NB_ADD-(NBI_ADD-NBI_OUTPUT) - 1 -: NB_OUTPUT] :
                     (sum[NB_ADD-1]) ? {{1'b1},{NB_OUTPUT-1{1'b0}}} : {{1'b0},{NB_OUTPUT-1{1'b1}}};


/*********************************************************************************/
/*                                   HARCODED COEF INITIALIZATION EXAMPLE        */
/*********************************************************************************/

// wire signed [ NB_COEFF - 1 : 0 ] coeff [ 23 : 0 ]; //! Matrix for Coefficients
// 
// assign coeff[0]  = 8'b0000_0000;   //[-1 1/2 1/4 1/8 1/16 1/32 1/64 1/128]
// assign coeff[1]  = 8'b0000_0000;
// assign coeff[2]  = 8'b0000_0000;
// assign coeff[3]  = 8'b0000_0000;
// 
// assign coeff[4]  = 8'b1111_1111;
// assign coeff[5]  = 8'b1110_1100;
// assign coeff[6]  = 8'b1111_1100;
// assign coeff[7]  = 8'b1111_1100;
// 
// assign coeff[8]  = 8'b0000_0000;
// assign coeff[9]  = 8'b0101_0000;
// assign coeff[10] = 8'b0001_0011;
// assign coeff[11] = 8'b0001_1100;
// 
// assign coeff[12] = 8'b0010_0000;
// assign coeff[13] = 8'b0001_1100;
// assign coeff[14] = 8'b0001_0011;
// assign coeff[15] = 8'b0101_0000;
// 
// assign coeff[16] = 8'b1111_1111;
// assign coeff[17] = 8'b1111_1100;
// assign coeff[18] = 8'b1111_1100;
// assign coeff[19] = 8'b1110_1100;
// 
// assign coeff[20] = 8'b0000_0000;
// assign coeff[21] = 8'b0000_0000;
// assign coeff[22] = 8'b0000_0000;
// assign coeff[23] = 8'b0000_0000;

endmodule

