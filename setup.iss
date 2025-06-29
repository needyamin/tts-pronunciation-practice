[Setup]
AppName=TTS Pronunciation Practice
AppVersion=1.0
AppPublisher=needyamin
AppPublisherURL=https://github.com/needyamin/tts-pronunciation-practice
AppSupportURL=https://github.com/needyamin/tts-pronunciation-practice/issues
AppUpdatesURL=https://github.com/needyamin/tts-pronunciation-practice
DefaultDirName={autopf}\TTS Pronunciation Practice
DefaultGroupName=TTS Pronunciation Practice
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=TTS_Pronunciation_Practice_Setup
SetupIconFile=y_icon_temp.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\TTS_Pronunciation_Practice.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "cmudict-0.7b-ipa.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "y_icon_temp.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TTS Pronunciation Practice"; Filename: "{app}\TTS_Pronunciation_Practice.exe"
Name: "{group}\{cm:UninstallProgram,TTS Pronunciation Practice}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\TTS Pronunciation Practice"; Filename: "{app}\TTS_Pronunciation_Practice.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\TTS Pronunciation Practice"; Filename: "{app}\TTS_Pronunciation_Practice.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\TTS_Pronunciation_Practice.exe"; Description: "{cm:LaunchProgram,TTS Pronunciation Practice}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
