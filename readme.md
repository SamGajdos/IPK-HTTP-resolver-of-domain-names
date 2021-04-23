# HTTP resolver doménových jmen
Vitajte v popise k prvému projektu z predmetu: **IPK - Počítačové komunikace a sítě**.
Jedná sa o implementáciu servera (*src/server.py*), ktorý ponúka preklad doménových mien. Server komunikuje pomocou protokolu HTTP. Server je implementovaný v jazyku Python 3.


## Spustenie
Server sa spúšťa pomocou príkazu: *make run=PORT*
Súbor *makefile* podáva tento port programu ako argument.
Ten sa následne kontroluje, či sa jedná o celé číslo v intervale (1023;65536) inak program vyhodí chybu a ukončí sa.
Ak je v parametri *PORT* viac číselných údajov oddelených medzerou, program bude brať do úvahy iba "prvý" údaj.


## Operácie

Server podporuje operácie *GET* a *POST*:
Ak sa nejedná o podporovanú operáciu, prípadne zle napísanú, server vráti: *405 Method Not Allowed.* 

### GET
parametre sú:
- name = doménové meno alebo IP adresa
- type = typ požadovanej odpovede (A alebo PTR)

Server vráti *400 Bad Request.* ak nastane minimálne jeden z týchto prípadov:
- parametre sú formálne nesprávne napísané(je tam niečo iné ako 'name=' alebo 'type=')
- type nesúhlasí s A alebo PTR 
- name má formálne nesprávne napísanú doménu
- chýba jeden alebo všetky požadované parametre

Ak sa v parametroch nachádza viac parametrov name= alebo type=, server bude prekladať prvý napísaný name s prvým napísaným type

V prípade nájdenia odpovede bude výsledok *200 OK.* Ak nie je odpoveď nájdená potom je odpoveď *404 Not Found.*

### POST
Formát:
DOTAZ:TYP

Server vráti *400 Bad Request.* ak nastane minimálne jeden z týchto prípadov:
- Formát je formálne nesprávne napísaný (neobsahuje ':') 
- DOTAZ alebo TYP sú formálne nesprávne napísané
- TYP nesedí s daným DOTAZOM
- V správe sa nachádzajú prázdne riadky (výnimka je posledný prázdny riadok)

Server vráti *404 Not Found.* ak nastane minimálne jeden z týchto prípadov:
- Telo správy bude prázdne
- Nepodarilo sa preložiť ani jeden dotaz

Server bude ignorovať dotaz z tela správy v prípade, že pre daný dotaz nebola nájdená odpoveď. Ak však ani jeden z dotazov sa nepodarí preložiť, server vráti *404 Not Found.*

V prípade nájdenia aspoň jednej odpovede bez chybných stavov bude výsledok *200 OK.* 

