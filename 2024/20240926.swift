class DeviceActivityModel: ObservableObject {
    let store = DeviceActivityReportManager()
    
    func requestAuthorization() {
        Task {
            do {
                try await store.requestAuthorization(toShare: [], toRead: [.applications])
                print("Authorization granted")
            } catch {
                print("Authorization failed: \(error.localizedDescription)")
            }
        }
    }
    
    func exportScreenTimeData() {
        Task {
            let now = Date()
            let startOfDay = Calendar.current.startOfDay(for: now)
            
            let interval = DateInterval(start: startOfDay, end: now)
            
            do {
                let data = try await store.data(for: interval)
                let csvString = self.convertToCSV(data: data)
                try self.saveToICloud(csvString: csvString)
                print("Data exported successfully")
            } catch {
                print("Failed to export data: \(error.localizedDescription)")
            }
        }
    }
    
    func convertToCSV(data: DeviceActivityData) -> String {
        var csv = "App Bundle ID,Total Time (seconds)\n"
        
        for (bundleID, usage) in data.applicationUsage {
            let totalTime = usage.totalTime
            csv += "\(bundleID),\(totalTime)\n"
        }
        
        return csv
    }
    
    func saveToICloud(csvString: String) throws {
        let fileManager = FileManager.default
        guard let iCloudURL = fileManager.url(forUbiquityContainerIdentifier: nil)?.appendingPathComponent("Documents/ScreenTimeData.csv") else {
            throw NSError(domain: "iCloud not available", code: 1, userInfo: nil)
        }
        
        try csvString.write(to: iCloudURL, atomically: true, encoding: .utf8)
    }
}
