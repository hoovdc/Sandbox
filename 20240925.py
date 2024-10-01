//Since Google Sheets doesn't allow syncing data with a XLSX format spreadsheet that is stored in Google Drive, 
//This file copies the XLSX data to a temp spreadsheet and then writes it to the desired destination Google Sheet
//Code originally drafted by ChatGPT o1-preview

function importExcelToSheet() {
  // IDs and Names (Replace with your actual IDs and sheet names)
  var excelFileId = 'YOUR_XLSX_FILE_ID'; // Original Excel file ID
  var destinationSpreadsheetId = 'YOUR_DESTINATION_SPREADSHEET_ID'; // Destination Google Sheet ID
  var destinationSheetName = 'YOUR_SHEET_NAME'; // Destination sheet name
  
  // Access the destination spreadsheet and sheet
  var destinationSpreadsheet = SpreadsheetApp.openById(destinationSpreadsheetId);
  var destinationSheet = destinationSpreadsheet.getSheetByName(destinationSheetName);
  
  // Clear existing data in the destination sheet
  destinationSheet.clearContents();
  
  // Step 1: Access the original Excel file
  var excelFile = DriveApp.getFileById(excelFileId);
  
  // Step 2: Create a copy of the file's data (Copy happens here)
  var excelBlob = excelFile.getBlob();
  
  // Step 3: Prepare the resource and options for conversion
  var resource = {
    title: excelFile.getName(), // Name of the new file
    mimeType: MimeType.GOOGLE_SHEETS // Target format
  };
  var optionalArgs = {
    convert: true // Instruct to convert upon insertion
  };
  
  // Step 4: Insert the copy and convert it (Conversion happens here)
  var temporarySpreadsheetFile = Drive.Files.insert(resource, excelBlob, optionalArgs);
  
  // Step 5: Open the converted (temporary) Google Sheets file
  var temporarySpreadsheet = SpreadsheetApp.openById(temporarySpreadsheetFile.id);
  var temporarySheet = temporarySpreadsheet.getSheets()[0]; // Assumes data is in the first sheet
  
  // Step 6: Get data from the temporary sheet
  var dataRange = temporarySheet.getDataRange();
  var dataValues = dataRange.getValues();
  
  // Step 7: Write data to the destination sheet
  var destinationRange = destinationSheet.getRange(1, 1, dataValues.length, dataValues[0].length);
  destinationRange.setValues(dataValues);
  
  // Step 8: Delete the temporary spreadsheet file
  DriveApp.getFileById(temporarySpreadsheetFile.id).setTrashed(true);
}
