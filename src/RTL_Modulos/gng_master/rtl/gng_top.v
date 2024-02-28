//------------------------------------------------------------------------------
//
// gng_top.v
//
//------------------------------------------------------------------------------

`timescale 1 ns / 1 ps

module gng_top #(
    parameter INIT_Z1 = 64'd5030521883283424767,
    parameter INIT_Z2 = 64'd18445829279364155008,
    parameter INIT_Z3 = 64'd18436106298727503359
)
(
    //! outputs
    output wire [15:0] o_data            , // output data, s<16,11>
    output wire        o_valid           , // output data valid
    // ! inputs
    input wire         i_clock_enable    , // clock enable
    input wire  [ 3:0] i_shifter_divider , // divide o_data para obtener una salida escalada 
    // clock and reset
    input wire         i_clock           , // system clock
    input wire         i_reset             // system synchronous reset, active low
);

//#######################################################################
//                    RESET                                            ##
//####################################################################### 
    wire   internal_reset           ;
    assign internal_reset = ~i_reset;
//#######################################################################
//                    INSTANCE_GNG                                     ##
//####################################################################### 
    wire [15:0] data ;
    wire        valid;

    gng #(
    .INIT_Z1(INIT_Z1),
    .INIT_Z2(INIT_Z2),
    .INIT_Z3(INIT_Z3)
    )
    u_gng 
    (
        // System signals
        .clk      (i_clock       ),      
        .rstn     (internal_reset),      

        // Data interface
        .ce       (i_clock_enable),      
        .valid_out(valid         ),      
        .data_out (data          )       
    );

//#######################################################################
//                    OUTPUT_ASSIGNMENTS                               ##
//####################################################################### 
    assign o_data  = data >> i_shifter_divider ; //se conserva el signo y se divide en funcion de la entrada
    assign o_valid = valid                     ;

endmodule
