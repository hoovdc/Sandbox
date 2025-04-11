/**
 * This script hides all columns from column A up to column KO (295th column)
 * that do not have any data in row 1.
 *
 * Steps:
 * 1. Get the active sheet and define the last column to check (295 for column KO).
 * 2. Get the values in row 1 from column A to KO.
 * 3. Loop through each column in row 1.
 * 4. If the cell in row 1 is empty, hide that column.
 *
 * Usage:
 * - Open the Google Sheets document where you want to use this script.
 * - Go to Extensions > Apps Script, paste this code, and save it.
 * - Run the function `hideEmptyColumnsUpToKO` to hide the empty columns.
 */
function hideEmptyColumnsUpToKO() {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastColumn = 295; // KO is the 295th column
    var range = sheet.getRange(1, 1, 1, lastColumn);
    var values = range.getValues()[0];
  
    for (var i = 0; i < values.length; i++) {
      var column = i + 1;
      if (values[i] === "") {
        sheet.hideColumns(column);
      }
    }
  }