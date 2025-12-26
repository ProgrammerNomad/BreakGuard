; BreakGuard Installer Script for Inno Setup
; Creates a professional Windows installer with update support

#define MyAppName "BreakGuard"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ProgrammerNomad"
#define MyAppURL "https://github.com/ProgrammerNomad/BreakGuard"
#define MyAppExeName "BreakGuard.exe"
#define MyAppId "{{B8F3A9C0-1234-5678-9ABC-DEF012345678}"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist\installer
OutputBaseFilename=BreakGuard_Setup_v{#MyAppVersion}
SetupIconFile=assets\logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Health Guardian - Enforces Healthy Work Breaks
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non-administrative install mode
;PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Start BreakGuard automatically when Windows starts"; GroupDescription: "Startup Options:"; Flags: checkedonce

[Files]
; Main executable and dependencies from PyInstaller output
Source: "dist\BreakGuard\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\BreakGuard\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Dirs]
; Create user data directory with full permissions
Name: "{app}\data"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Add to Windows startup if selected
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "BreakGuard"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
; Offer to launch application after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up log files on uninstall (but preserve user data)
Type: filesandordirs; Name: "{app}\logs"

[Code]
var
  DataDirPage: TInputDirWizardPage;
  PreserveDataCheckBox: TNewCheckBox;
  OldInstallPath: String;
  IsUpgrade: Boolean;

function GetOldInstallPath(Param: String): String;
begin
  Result := OldInstallPath;
end;

function IsUpgradeInstall: Boolean;
begin
  Result := IsUpgrade;
end;

// Check if this is an upgrade
function InitializeSetup(): Boolean;
var
  UninstallKey: String;
  InstallPath: String;
begin
  Result := True;
  IsUpgrade := False;
  OldInstallPath := '';
  
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1';
  
  // Check if already installed
  if RegQueryStringValue(HKLM, UninstallKey, 'InstallLocation', InstallPath) or
     RegQueryStringValue(HKCU, UninstallKey, 'InstallLocation', InstallPath) then
  begin
    OldInstallPath := InstallPath;
    IsUpgrade := True;
    
    // Show upgrade message
    if MsgBox('BreakGuard is already installed.' + #13#10#13#10 + 
              'Your settings and data will be preserved.' + #13#10#13#10 +
              'Continue with upgrade?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

// Backup user data before installation
procedure BackupUserData();
var
  SourcePath, BackupPath: String;
begin
  if IsUpgrade and (OldInstallPath <> '') then
  begin
    SourcePath := OldInstallPath + '\data';
    BackupPath := ExpandConstant('{tmp}\breakguard_backup');
    
    if DirExists(SourcePath) then
    begin
      Log('Backing up user data from: ' + SourcePath);
      
      // Create backup directory
      CreateDir(BackupPath);
      
      // Copy data files
      if FileCopy(SourcePath + '\app_state.json', BackupPath + '\app_state.json', False) then
        Log('Backed up: app_state.json');
        
      if FileCopy(SourcePath + '\face_encodings.json', BackupPath + '\face_encodings.json', False) then
        Log('Backed up: face_encodings.json');
        
      if FileCopy(SourcePath + '\totp_secret.enc', BackupPath + '\totp_secret.enc', False) then
        Log('Backed up: totp_secret.enc');
        
      if FileCopy(OldInstallPath + '\config.json', BackupPath + '\config.json', False) then
        Log('Backed up: config.json');
    end;
  end;
end;

// Restore user data after installation
procedure RestoreUserData();
var
  BackupPath, DestPath: String;
begin
  if IsUpgrade then
  begin
    BackupPath := ExpandConstant('{tmp}\breakguard_backup');
    DestPath := ExpandConstant('{app}\data');
    
    if DirExists(BackupPath) then
    begin
      Log('Restoring user data to: ' + DestPath);
      
      // Restore data files
      if FileExists(BackupPath + '\app_state.json') then
        FileCopy(BackupPath + '\app_state.json', DestPath + '\app_state.json', False);
        
      if FileExists(BackupPath + '\face_encodings.json') then
        FileCopy(BackupPath + '\face_encodings.json', DestPath + '\face_encodings.json', False);
        
      if FileExists(BackupPath + '\totp_secret.enc') then
        FileCopy(BackupPath + '\totp_secret.enc', DestPath + '\totp_secret.enc', False);
        
      if FileExists(BackupPath + '\config.json') then
        FileCopy(BackupPath + '\config.json', ExpandConstant('{app}\config.json'), False);
        
      Log('User data restored successfully');
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // Backup data before installation
    BackupUserData();
  end;
  
  if CurStep = ssPostInstall then
  begin
    // Restore data after installation
    RestoreUserData();
  end;
end;

// Custom uninstall page
procedure InitializeUninstallProgressForm();
begin
  UninstallProgressForm.Caption := 'Uninstall BreakGuard';
end;

function InitializeUninstall(): Boolean;
var
  Response: Integer;
  AppDataPath: String;
begin
  Result := True;
  
  // Get AppData path where actual user data is stored
  AppDataPath := ExpandConstant('{localappdata}\BreakGuard');
  
  // Ask if user wants to keep data
  Response := MsgBox('Do you want to keep your BreakGuard settings and data?' + #13#10#13#10 +
                     'This includes:' + #13#10 +
                     '• Work/break interval settings' + #13#10 +
                     '• TOTP authentication setup' + #13#10 +
                     '• Face recognition data' + #13#10 +
                     '• Application logs' + #13#10#13#10 +
                     'Choose Yes to keep settings for future installation.' + #13#10 +
                     'Choose No to completely remove everything.',
                     mbConfirmation, MB_YESNO or MB_DEFBUTTON1);
  
  if Response = IDYES then
  begin
    // Keep data - don't delete AppData directory
    Log('User chose to keep settings and data at: ' + AppDataPath);
  end
  else
  begin
    // Delete everything from AppData
    if DirExists(AppDataPath) then
    begin
      DelTree(AppDataPath, True, True, True);
      Log('Deleted all user data from: ' + AppDataPath);
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Kill any running BreakGuard processes
    Exec('taskkill', '/F /IM BreakGuard.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    Log('Uninstall completed');
  end;
end;
