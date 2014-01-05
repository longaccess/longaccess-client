namespace csharp ThriftInterface
//============Errors====================
enum ErrorType {
  NoError = 0,
  Server = 1,
  Network = 2,
  Authentication = 3,
  Validation = 4,
  Other = 5,
  NotImplemented = 6,
  FileNotFound = 7
}
exception InvalidOperation {
  1: ErrorType what,
  2: string why,
  3: optional string filename
}
struct DateInfo {
  1: i32 Day,
  2: i32 Month,
  3: i32 Year,
  4: i32 Hour,
  5: i32 Minutes,
  6: i32 Seconds
}
//===========Structures=================
enum ArchiveStatus {
  Completed = 0,
  InProgress = 1,
  Paused=2,
  Stopped= 3,
  Failed = 4,
  Local = 5
}
struct TransferStatus {
  1: string StatusDescription, 
  2: string ETA,
  3: i64 RemainingBytes,
  4: double Progress,
  5: ArchiveStatus Status
}
struct ArchiveInfo {
  1: string Title,
  2: string Description,
  3: i64 SizeInBytes,
  4: DateInfo CreatedDate,
  5: string Md5HexDigits,
}
struct Capsule {
  1: string Created,
  2: string ID,
  3: string Resource_URI,
  4: string Title,
  5: string User,
  6: DateInfo ExpirationDate,
  7: i64 TotalSizeInBytes,
  8: i64 AvailableSizeInBytes,
  9: list<ArchiveInfo> CapsuleContents
}
struct Archive {
  1: string LocalID,  
  2: ArchiveStatus Status, 
  3: ArchiveInfo Info
}
struct Signature {
  1: string ArchiveID,
  2: DateInfo DateCreated,
  3: string UploaderName,
  4: string UploaderEmail
}
struct Certificate {
  1: string HexDigitsKey,
  2: Signature Sig,
  3: ArchiveInfo RelatedArchive,
  4: string LocalID
}
struct Settings
{
  1: string StoredUserName,
  2: string StoredPassword,
  3: bool RememberMe,
  4: string ArchivesFolder,
  5: string CertificatesFolder
}
enum CertExportFormat
{
  HTML = 0,
  YAML = 1,
  PDF = 2
}
struct VersionInfo
{
  1: string version,
  2: string description,
  3: string uri
}
//===========Methods===================
service CLI {

  bool PingCLI(), //if it returns false the it will close and restart

  void CloseWhenPossible(),

  bool LoginUser(1: string username, 2: string Pass,3: bool Remember) throws (1:InvalidOperation error),

  bool UserIsLoggedIn(),
  
  bool Logout() throws (1:InvalidOperation error),  
  
  list<Capsule> GetCapsules() throws (1:InvalidOperation error),
  
  Archive CreateArchive(1: list<string> filePaths) 
  throws (1: InvalidOperation error),

  list<Archive> GetUploads(),
  
  void UploadToCapsule(1: string ArchiveLocalID, 2: string CapsuleID, 3: string title, 4: string description) throws (1:InvalidOperation error),

  void ResumeUpload(1: string ArchiveLocalID) throws (1:InvalidOperation error),
  
  TransferStatus QueryArchiveStatus(1: string ArchiveLocalID) throws (1:InvalidOperation error),
  
  void PauseUpload(1: string ArchiveLocalID) throws (1:InvalidOperation error),    
  
  void CancelUpload(1: string ArchiveLocalID) throws (1:InvalidOperation error),  
  
  list<Certificate> GetCertificates(),
   
  binary ExportCertificate(1: string ArchiveID,2: CertExportFormat format) throws (1:InvalidOperation error), 

  void Decrypt(1: string archivePath,2: string key,3: string destinationPath) throws (1:InvalidOperation error)  
  
  Settings GetSettings(),

  void SetSettings(1: Settings settings),

  VersionInfo GetLatestVersion(),

  VersionInfo GetVersion(),
}
