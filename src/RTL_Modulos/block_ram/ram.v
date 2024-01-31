
//  Xilinx Single Port No Change RAM
//  This code implements a parameterizable single-port no-change memory where when data is written
//  to the memory, the output remains unchanged.  This is the most power efficient write mode.
//  If a reset or enable is not necessary, it may be tied off or removed from the code.

module xilinx_single_port_ram_no_change 
#(
  parameter RAM_WIDTH = 18,                       // Specify RAM data width
  parameter RAM_DEPTH = 1024,                     // Specify RAM depth (number of entries)
  parameter RAM_PERFORMANCE = "HIGH_PERFORMANCE", // Select "HIGH_PERFORMANCE" or "LOW_LATENCY"
  parameter INIT_FILE = ""                        // Specify name/location of RAM initialization file if using one (leave blank if not)
) (
  input [clogb2(RAM_DEPTH-1)-1:0] address_bus,    // Address bus, width determined from RAM_DEPTH
  input [RAM_WIDTH-1:0] data_input,               // RAM input data
  input clock,                                    // Clock
  input write_enable,                             // Write enable
  input enable,                                   // RAM Enable, for additional power savings, disable port when not in use
  input reset,                                    // Output reset (does not affect memory contents)
  input register_enable,                          // Output register enable
  output [RAM_WIDTH-1:0] data_output              // RAM output data
);

  reg [RAM_WIDTH-1:0] BRAM [RAM_DEPTH-1:0];
  reg [RAM_WIDTH-1:0] ram_data = {RAM_WIDTH{1'b0}};

  // The following code either initializes the memory values to a specified file or to all zeros to match hardware
  generate
    if (INIT_FILE != "") begin: use_init_file
      initial
        $readmemh(INIT_FILE, BRAM, 0, RAM_DEPTH-1);
    end else begin: init_bram_to_zero
      integer ram_index;
      initial
        for (ram_index = 0; ram_index < RAM_DEPTH; ram_index = ram_index + 1)
          BRAM[ram_index] = {RAM_WIDTH{1'b0}};
    end
  endgenerate

  always @(posedge clock)
    if (enable)
      if (write_enable)
        BRAM[address_bus] <= data_input;
      else
        ram_data <= BRAM[address_bus];

  //  The following code generates HIGH_PERFORMANCE (use output register) or LOW_LATENCY (no output register)
  generate
    if (RAM_PERFORMANCE == "LOW_LATENCY") begin: no_output_register

      // The following is a 1 clock cycle read latency at the cost of a longer clock-to-out timing
       assign data_output = ram_data;

    end else begin: output_register

      // The following is a 2 clock cycle read latency with improve clock-to-out timing

      reg [RAM_WIDTH-1:0] data_output_reg = {RAM_WIDTH{1'b0}};

      always @(posedge clock)
        if (reset)
          data_output_reg <= {RAM_WIDTH{1'b0}};
        else if (register_enable)
          data_output_reg <= ram_data;

      assign data_output = data_output_reg;

    end
  endgenerate

  //  The following function calculates the address width based on specified RAM depth
  function integer clogb2;
    input integer depth;
      for (clogb2=0; depth>0; clogb2=clogb2+1)
        depth = depth >> 1;
  endfunction

endmodule

// The following is an instantiation template for xilinx_single_port_ram_no_change
/*
  //  Xilinx Single Port No Change RAM
  xilinx_single_port_ram_no_change #(
    .RAM_WIDTH(18),                       // Specify RAM data width
    .RAM_DEPTH(1024),                     // Specify RAM depth (number of entries)
    .RAM_PERFORMANCE("HIGH_PERFORMANCE"), // Select "HIGH_PERFORMANCE" or "LOW_LATENCY" 
    .INIT_FILE("")                        // Specify name/location of RAM initialization file if using one (leave blank if not)
  ) your_instance_name (
    .address_bus(address_bus),    // Address bus, width determined from RAM_DEPTH
    .data_input(data_input),      // RAM input data, width determined from RAM_WIDTH
    .clock(clock),      // Clock
    .write_enable(write_enable),        // Write enable
    .ena(ena),        // RAM Enable, for additional power savings, disable port when not in use
    .reset(reset),      // Output reset (does not affect memory contents)
    .register_enable(register_enable),  // Output register enable
    .data_output(data_output)     // RAM output data, width determined from RAM_WIDTH
  );

*/
						
						