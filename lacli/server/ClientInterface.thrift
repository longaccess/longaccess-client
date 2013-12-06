namespace csharp ThriftInterface
//============Errors====================
enum ErrorType {
  NoError = 0,
  Server = 1,
  nNetwork = 2,
  Authentication = 3,
  Validation = 4,
  Other = 5
}
exception InvalidOperation {
  1: ErrorType what,
  2: string why
}
struct DateInfo {
  1: i32 Day,
  2: i32 Month,
  3: i32 Year
}
//===========Structures=================
struct TransferStatus {
  1: string StatusDescription, 
  2: string ETA,
  3: i32 RemainingMB,
  4: double Progress
}
struct Capsule {
  1: string Created,
  2: string ID,
  3: string Resource_URI,
  4: string Title,
  5: string User,
  6: DateInfo ExpirationDate
}
struct Archive {
  1: string ID,
  2: string Title
}
struct Certificate {
  1: string Title,
  2: string Description,
  3: string HexDigitsKey
}


//===========Methods===================
service CLI {

  void PingCLI(),

  bool LoginUser(1: string username, 2: string Pass,3: bool Remember) throws (1:InvalidOperation error),
  
  bool Logout() throws (1:InvalidOperation error),  
  
  list<Capsule> GetCapsules() throws (1:InvalidOperation error),
  
  Archive UploadFileGUI(1: list<string> filePaths,2: string capsuleID, 3: string title, 4: string description) 
  throws (1: InvalidOperation error),

  list<Archive> GetIncompleteUploads(),
  
  void BeginUpload(1: string ArchiveID),

  void ResumeUpload(1: string ArchiveID),
  
  TransferStatus QueryArchiveStatus(1: string ArchiveID),
  
  void PauseUpload(1: string ArchiveID),    
  
  void CancelUpload(1: string ArchiveID),  
  
  list<Certificate> getCertificates(),
  
  string GetCertificateFolder(),
  
  void SetCertificateFolder(1: string path),
  
  binary Export(1: string certificateID,2: string format), //format??
  
  void Decrypt(1: string archivePath,2: string key,3: string destinationPath)  
  
}


