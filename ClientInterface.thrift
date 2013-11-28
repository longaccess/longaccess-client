
//===========Structures=================
struct TranferStatus {
  1: SomeException Error,
  2: string ETA,
  3: int32 Remaining MB,
  4: double Progress
}
struct Capsule {
  1: string Created,
  2: string ID,
  3: string Resource_URI,
  4: string Title,
  5: string User,
  6: DateTime Expires
}
struct Archive {
  1: string ID,
}


//===========Methods===================
service LongAccessClient {
  bool LoginUser(string username,string Pass, bool Remember) throws (1:SomeException error),
  
  bool Logout() throws (1:SomeException error),
  
  
  list<Capsule> GetCapsules() throws (1:SomeException error)  throws (1:SomeException error),
  
  Archive UploadFileGUI(list<string> filePaths,string capsuleID, string title,string description) 
  throws (1:SomeException error),
  
  void GeginUpload(string ArchiveID),
  
  TransferStatus QueryArchiveStatus(string ArchiveID),
  
  void PauseUpload(string ArchiveID),
  
  void ResumeUpload(string ArchiveID),
  
  void CancelUpload(string ArchiveID)
  
  
  list<Certificates> getCertificates(),
  
  string GetCertificateFolder(),
  
  void SetCertificateFolder(string path),
  
  binary Export(string certificateID,string format), //format??
  
  void Decrypt(archivePath, key, destinationPath)
  
  
}


//============Errors====================
enum ErrorTypes {
  ADD = 1,
  SUBTRACT = 2,
  MULTIPLY = 3,
  DIVIDE = 4
}
exception SomeException {
  1: ErrorTypes ErrorType,
  2: string why
}
