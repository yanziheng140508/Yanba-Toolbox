[Setup]
AppName=闫巴工具箱
AppVersion=YBv1.2
AppPublisher=闫巴
DefaultDirName={autopf}\闫巴工具箱
DefaultGroupName=闫巴工具箱
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=闫巴工具箱_YBv1.2_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64os
ArchitecturesAllowed=x64compatible
UninstallDisplayIcon={app}\闫巴工具箱_YBv1.1.exe
UninstallDisplayName=闫巴工具箱 YBv1.2
SetupIconFile=icon.ico

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"
Name: "startupicon"; Description: "开机自动启动"; GroupDescription: "附加任务:"

[Files]
Source: "dist\闫巴工具箱_YBv1.1.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\闫巴工具箱"; Filename: "{app}\闫巴工具箱_YBv1.1.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\卸载闫巴工具箱"; Filename: "{uninstallexe}"
Name: "{autodesktop}\闫巴工具箱"; Filename: "{app}\闫巴工具箱_YBv1.1.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{autostartup}\闫巴工具箱"; Filename: "{app}\闫巴工具箱_YBv1.1.exe"; IconFilename: "{app}\icon.ico"; Tasks: startupicon

[Run]
Filename: "{app}\闫巴工具箱_YBv1.1.exe"; Description: "立即启动闫巴工具箱"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM 闫巴工具箱_YBv1.1.exe"; Flags: runhidden; RunOnceId: "KillProcess"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\yanba_data"
