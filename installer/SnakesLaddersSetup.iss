; Inno Setup script adjusted for this repo
#define MyAppName "Snake and Ladder Road Safety Edition"
#define MyAppVersion "1.5"
#define MyAppPublisher "Ishant's tech"
#define MyAppExeName "SnakesLadders.exe"

[Setup]
AppId={{1228ECCA-2D49-4AC9-9595-4FA816F6FE02}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
LicenseFile={#SourcePath}\..\..\license.txt
InfoBeforeFile={#SourcePath}\..\..\README.txt
InfoAfterFile={#SourcePath}\..\..\THANKYOU.txt
OutputDir={#SourcePath}\..\dist\installer
SetupIconFile={#SourcePath}\..\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Expect the executable at new/dist/SnakesLadders.exe after build
Source: "{#SourcePath}\..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
