; Script Inno Setup para Astisan Orçamentos
; Versão Corrigida (Executando de dentro da pasta do projeto)

[Setup]
; Informações básicas
AppName=Artisan Orçamentos
AppVersion=2.3.4
AppPublisher=Artisan
; AppPublisherURL=http://www.seu-site-aqui.com
; AppSupportURL=http://www.seu-site-aqui.com

; Diretório de instalação (em Program Files)
DefaultDirName={autopf}\Artisan Orçamentos
; Pasta no Menu Iniciar
DefaultGroupName=Artisan Orçamentos
; Não permitir que o utilizador mude o nome da pasta do Menu Iniciar
DisableProgramGroupPage=yes

; Ficheiro de saída (o setup.exe)
OutputBaseFilename=Artisan
; Onde guardar o setup.exe (cria uma pasta 'instalador' DENTRO de Projeto_Artisan)
OutputDir=instalador
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Pedir privilégios de Admin (necessário para Program Files)
PrivilegesRequired=admin

; *** ALTERADO: Removido "Projeto_Artisan\" ***
SetupIconFile=icone.ico

[Languages]
; Incluir idioma Português (Brasil)
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
; Checkbox para "Criar um ícone no Ambiente de Trabalho"
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. O EXECUTÁVEL (da pasta dist, que está na pasta atual)
Source: "dist\Artisan.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. O ÍCONE (que está na pasta atual)
; *** ALTERADO: Removido "Projeto_Artisan\" ***
Source: "icone.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Ícone no Menu Iniciar (usa o icone.ico que foi copiado para {app})
Name: "{group}\Artisan Orçamentos"; Filename: "{app}\Artisan.exe"; IconFilename: "{app}\icone.ico"

; Ícone no Ambiente de Trabalho
Name: "{autodesktop}\Artisan Orçamentos"; Filename: "{app}\Artisan.exe"; Tasks: "desktopicon"; IconFilename: "{app}\icone.ico"

[Run]
; Executar a aplicação no final da instalação
Filename: "{app}\Artisan.exe"; Description: "{cm:LaunchProgram,Artisan Orçamentos}"; Flags: nowait postinstall skipifsilent