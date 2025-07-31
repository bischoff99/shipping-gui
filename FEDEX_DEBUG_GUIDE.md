# FedEx Shipping Function Debug Guide

This guide explains how to debug the `create_fedex_shipment` function in `fedex_orders.py` using the integrated debugging setup.

## Quick Start

1. **Activate debug breakpoints:**
   ```bash
   python debug_fedex_shipping.py --activate
   ```

2. **Run test with debugging:**
   ```bash
   python debug_fedex_shipping.py --test
   ```

3. **Deactivate breakpoints when done:**
   ```bash
   python debug_fedex_shipping.py --deactivate
   ```

## Debug Breakpoints

The function has 6 strategic breakpoints to inspect key variables:

### Breakpoint 1: Function Entry
**Location:** Start of `create_fedex_shipment`
**Variables to inspect:**
- `customer_data` - Input customer information
- `origin_address_id` - Origin address parameter

### Breakpoint 2: Origin Address Resolution
**Location:** After address resolution logic
**Variables to inspect:**
- `origin_address_id` - Resolved address ID
- `addresses` - Available addresses from API

### Breakpoint 3: Product Retrieval
**Location:** After getting products
**Variables to inspect:**
- `products` - Retrieved products list
- Product structure and contents

### Breakpoint 4: Customer Data Formatting
**Location:** After data normalization
**Variables to inspect:**
- `formatted_customer` - Normalized customer data
- Comparison with original `customer_data`

### Breakpoint 5: API Response
**Location:** After shipment creation
**Variables to inspect:**
- `result` - Complete API response
- Response structure and shipment ID

### Breakpoint 6: FedEx Booking
**Location:** After FedEx rate booking
**Variables to inspect:**
- `fedex_booking` - Booking response
- `shipment_id` - ID used for booking

## PDB Commands Reference

### Navigation
- `l` or `list` - Show current code context
- `n` or `next` - Execute next line (don't step into functions)
- `s` or `step` - Step into function calls
- `c` or `continue` - Continue execution to next breakpoint
- `u` or `up` - Move up in call stack
- `d` or `down` - Move down in call stack

### Variable Inspection
- `p <variable>` - Print variable value
- `pp <variable>` - Pretty print variable (formatted)
- `type(<variable>)` - Show variable type
- `len(<variable>)` - Show variable length (if applicable)
- `dir(<variable>)` - Show variable attributes/methods
- `vars(<variable>)` - Show object's __dict__

### Environment Inspection
- `locals()` - Show all local variables
- `globals()` - Show all global variables
- `where` or `w` - Show current stack trace

### Control
- `q` or `quit` - Quit debugger (will raise exception)
- `r` or `return` - Continue until return from current function

## Debugging Scenarios

### Scenario 1: Customer Data Issues
If customer data appears malformed:
```python
# At breakpoint 1
p customer_data
pp customer_data
type(customer_data)
# Check for missing fields
p customer_data.get('name')
p customer_data.get('address_1')
```

### Scenario 2: Product Retrieval Problems
If no products are found:
```python
# At breakpoint 3
p products
p len(products) if products else "No products"
# Check API connection
p self.easyship_api
```

### Scenario 3: API Response Analysis
To understand API failures:
```python
# At breakpoint 5
pp result
# Check for error messages
p result.get('errors') if result else "No result"
p result.get('message') if result else "No result"
```

### Scenario 4: Booking Failures
If FedEx booking fails:
```python
# At breakpoint 6
pp fedex_booking
p shipment_id
# Check if shipment was created but booking failed
```

## Advanced Debugging

### Conditional Breakpoints
You can modify the breakpoint lines to be conditional:
```python
# Only break for specific customers
if customer_data.get('name') == 'Harry Armani':
    pdb.set_trace()
```

### Custom Variable Inspection
Add custom debug prints:
```python
# Add after any line
print(f"DEBUG: variable_name = {variable_name}")
```

### Logging Integration
The debug script preserves existing logging while adding PDB capability.

## Troubleshooting

### Common Issues

1. **Breakpoints not triggering:**
   - Ensure you ran `--activate` command
   - Check that the function is actually being called

2. **Import errors:**
   - Make sure you're in the correct directory
   - Check that required dependencies are installed

3. **API connection issues:**
   - Verify environment variables are set
   - Check network connectivity

### Debug Output Interpretation

The debug script adds structured output:
- 🔍 DEBUG messages show variable states
- ✅ Success indicators show progress
- ❌ Error indicators highlight issues

## Integration with MCP-PDB

While MCP-PDB tools are configured in the project (visible in `.claude/settings.local.json`), this debugging setup provides a standalone solution that works with standard Python PDB.

The debug breakpoints can be easily integrated with MCP-PDB when the server is active by using the MCP commands instead of manual PDB interaction.

## Best Practices

1. **Start with debug output first** - Run `--test` to see the flow before activating breakpoints
2. **Use targeted breakpoints** - Don't activate all at once initially
3. **Document findings** - Note variable states and API responses
4. **Clean up** - Always run `--deactivate` when finished
5. **Test incrementally** - Fix one issue at a time

## Safety Notes

- Breakpoints are automatically deactivated to prevent production issues
- Debug output is clearly marked with 🔍 prefix
- Original functionality is preserved when debugging is disabled