//! @title Control
//! @file Control.v
//! @author Advance Digital Design - Luis Soto
//! @date 22-08-2023
//! @version 1



module control
#(
  //!PARAMETERS
  parameter NB_PHASES     = 2
)
(
  //!INPUTS
  input wire                   i_reset,
  input wire                   i_clock,
  //!OUTPUTS
  output [ NB_PHASES - 1 : 0 ] o_control

);

    //!LOCALPARAMETER
    localparam MAX_COUNT = 2 ** NB_PHASES - 1 ;

    //!Variables
    reg [ NB_PHASES - 1 : 0 ] counter ;

    always @(posedge i_clock) begin
    
        if(i_reset || counter >= MAX_COUNT ) begin

            counter <= { NB_PHASES { 1'b0 } };

        end
        else begin

            counter <= counter + { { NB_PHASES - 1 { 1'b0 } }, 1'b1 };

        end

    end

  //! Continuous Assignments Output
  assign o_control   =  counter ;


  endmodule