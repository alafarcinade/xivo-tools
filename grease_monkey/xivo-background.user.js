// Copyright (C) 2015 Avencall
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>

// ==UserScript==
// @name        XiVO background
// @description Change the background of XiVO web-interface to quickly identify different servers.
// @namespace   http://xivo.io
// @include     https://assurancetourisk*
// @grant       none
// ==/UserScript==

document.getElementsByTagName('body')[0].style = 'background-color: #FA5B5A;';
