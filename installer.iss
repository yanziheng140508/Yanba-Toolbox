; 闫巴工具箱 YBv1.0 安装脚本
; Inno Setup 6

[Setup]
AppName=闫巴工具箱
AppVersion=YBv1.0
AppPublisher=闫巴
AppPublisherURL=https://github.com/yanba/toolbox
AppSupportURL=https://github.com/yanba/toolbox
AppUpdatesURL=https://github.com/yanba/toolbox
DefaultDirName={autopf}\闫巴工具箱
DefaultGroupName=闫巴工具箱
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=闫巴工具箱_YBv1.0_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64compatible
UninstallDisplayIcon={app}\闫巴工具箱.exe
UninstallDisplayName=闫巴工具箱 YBv1.0
SetupIconFile=icon.ico
LicenseFile=
InfoBeforeFile=

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"
Name: "startupicon"; Description: "开机自动启动"; GroupDescription: "附加任务:"

[Files]
Source: "dist\闫巴工具箱.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\闫巴工具箱"; Filename: "{app}\闫巴工具箱.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\卸载闫巴工具箱"; Filename: "{uninstallexe}"
Name: "{autodesktop}\闫巴工具箱"; Filename: "{app}\闫巴工具箱.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{autostartup}\闫巴工具箱"; Filename: "{app}\闫巴工具箱.exe"; IconFilename: "{app}\icon.ico"; Tasks: startupicon

[Run]
Filename: "{app}\闫巴工具箱.exe"; Description: "立即启动闫巴工具箱"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM 闫巴工具箱.exe"; Flags: runhidden; RunOnceId: "KillProcess"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\yanba_data"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
