//code in Google Apps Script to archive stock price data as a backup data source for when 
//the googlefinance() function fails in my sheet

function archiveFinancialMarketData() {
  const sheetName = 'Financial_Markets'; // Replace with your actual sheet name
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  const startRow = 4; // Starting row of the data (assuming row 3 has headers)
  
  // Determine the number of rows with date values in column H
  const dateRange = sheet.getRange('H4:H');
  const dateValues = dateRange.getValues().filter(String);
  const numRows = dateValues.length;

  // Fetch data range including index, date, and placeholders for prices (Columns G to K)
  const sourceRange = sheet.getRange(startRow, 7, numRows, 5); // Columns G to K (ignoring column H)
  const sourceData = sourceRange.getValues();

  // Log source data for the first row
  Logger.log('sourceData (first row): ' + JSON.stringify(sourceData[0]));

  // Stock symbols to fetch data for (from cells C1 to E1)
  const stockSymbolsRange = sheet.getRange('C1:E1');
  const stockSymbols = stockSymbolsRange.getValues()[0].map(symbol => symbol.toString().trim()).filter(symbol => symbol !== '');
  Logger.log('stockSymbols: ' + JSON.stringify(stockSymbols));

  // Prepare to update the archive data (columns I to K)
  const updatedArchiveData = [];

  sourceData.forEach((row, rowIndex) => {
    const index = row[0]; // Index #
    const date = row[1]; // Date from column H

    // Fetch NASDAQ price
    const nasdaqPrice = fetchHistoricalPrice(stockSymbols[0], date);
    // Fetch S&P price
    const spPrice = fetchHistoricalPrice(stockSymbols[1], date);
    // Fetch DJIA price
    const djiPrice = fetchHistoricalPrice(stockSymbols[2], date);

    // Update the row with new data (columns I to K)
    const updatedRow = [nasdaqPrice, spPrice, djiPrice];
    updatedArchiveData.push(updatedRow);

    // Log the update action
    Logger.log(`Updating archive for date ${date} with NASDAQ: ${nasdaqPrice}, S&P: ${spPrice}, DJIA: ${djiPrice}`);
  });

  // Log updated archive data for the first row
  Logger.log('updatedArchiveData (first row): ' + JSON.stringify(updatedArchiveData[0]));

  // Update the sheet with the new archive data (columns I to K only)
  const targetRange = sheet.getRange(startRow, 9, updatedArchiveData.length, 3); // Columns I to K
  targetRange.setValues(updatedArchiveData);
}

// Function to fetch historical price
function fetchHistoricalPrice(symbol, date) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Temporary');
  if (!sheet) {
    SpreadsheetApp.getActiveSpreadsheet().insertSheet('Temporary');
  }

  const dateFormatted = Utilities.formatDate(new Date(date), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const formula = `=GOOGLEFINANCE("${symbol}", "close", DATE(${dateFormatted.split('-').join(',')}))`;
  const tempCell = sheet.getRange('A1');
  tempCell.setFormula(formula);
  SpreadsheetApp.flush();
  
  // Introduce a pause to allow GOOGLEFINANCE to populate
  //Utilities.sleep(10000); // Wait 10 seconds before checking the value
  
  const cellValue = tempCell.getValue();
  const cellFormula = tempCell.getFormula();
  
  Logger.log(`Formula used: ${cellFormula}`);
  Logger.log(`Cell value type: ${typeof cellValue}`);
  Logger.log(`Cell value: ${JSON.stringify(cellValue)}`);
  
  // Handle different formats returned by GOOGLEFINANCE
  if (Array.isArray(cellValue) && cellValue.length > 1) {
    // If it's a table format, get the price from the second row
    const price = cellValue[1][1]; // Assuming the price is in the second row, second column
    Logger.log(`Extracted price from table: ${price}`);
    return price;
  } else if (typeof cellValue === 'string' && cellValue.startsWith('Date')) {
    // If it's the table format with headers, get the price from the second row
    const price = tempCell.offset(1, 1).getValue(); // Offset to get the price value
    Logger.log(`Extracted price from table with headers: ${price}`);
    return price;
  } else if (typeof cellValue === 'number') {
    // If it's a single numeric value, return it directly
    Logger.log(`Direct price value: ${cellValue}`);
    return cellValue;
  } else {
    Logger.log(`Failed to fetch price for ${symbol} on ${date}`);
    return null;
  }
}
