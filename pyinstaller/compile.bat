:: This file is part of the pyrmexplorer software that allows exploring
:: and downloading content stored on Remarkable tablets.
::
:: Copyright 2019 Nicolas Bruot (https://www.bruot.org/hp/)
::
::
:: pyrmexplorer is free software: you can redistribute it and/or modify
:: it under the terms of the GNU General Public License as published by
:: the Free Software Foundation, either version 3 of the License, or
:: (at your option) any later version.
::
:: pyrmexplorer is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
:: GNU General Public License for more details.
::
:: You should have received a copy of the GNU General Public License
:: along with pyrmexplorer.  If not, see <http://www.gnu.org/licenses/>.


:: Compiles a standalone executable for Windows of rMExplorer
::
:: Execute this batch script in a Python environment that can run both
:: rmexplorer and pyinstaller.


@echo off

setlocal
:PROMPT
SET /P ANSWER=Delete any previous compilation output? (Y/[N])
IF /I "%ANSWER%" NEQ "Y" GOTO END
IF EXIST build @RD /S /Q build
IF EXIST dist @RD /S /Q dist
IF EXIST rmexplorer.spec DEL rmexplorer.spec
:END
endlocal

pyinstaller --paths=.. ^
    --add-data ../README;. ^
    --add-data ../COPYING;. ^
    --add-binary ../rmexplorer/icon.ico;. ^
    --icon=../rmexplorer/icon.ico ^
    -n rmexplorer -w rmexplorer_pyi.py
