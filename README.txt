================================================================
  TARGUL CARTII - COS DE CUMPARATURI PARTAJABIL
  Descriere proiect si pasi de urmat
================================================================


CE FACE PROIECTUL
-----------------
Cand ai 250+ carti in cosul de pe targulcartii.ro, cosul expira
in 30 de minute. Nu poti trimite cuiva 250 de link-uri sa le
adauge manual in cos.

Acest proiect:
1. Salveaza lista de carti din cosul tau (link-uri permanente)
2. Extrage automat product_id-urile de pe fiecare pagina de carte
3. Genereaza o pagina web + script pe care le urci pe hostingul tau
4. Persoana care primeste link-ul (ex: Andreea) copiaza scriptul,
   il ruleaza pe targulcartii.ro, si toate cartile se adauga
   automat in cosul ei in ~2 minute (250 carti)


FISIERE PROIECT
---------------
D:\Targul Cartii\
  cart_manager.py          - Scriptul principal Python
  books.json               - Lista salvata de carti (generata automat)
  hosting\
    index.html             - Pagina web pentru Andreea (de urcat pe hosting)
    script.js              - Scriptul JS (backup, e inclus si in index.html)


CERINTE
-------
- Python 3.x instalat
- Biblioteca 'requests' (pip install requests)
- Cont pe targulcartii.ro
- Un hosting web (orice hosting, ex: site personal, GitHub Pages, etc.)


================================================================
  PASI DE URMAT
================================================================


PAS 1 - SALVEZI COSUL
----------------------
1. Logheaza-te pe https://www.targulcartii.ro/
2. Adauga toate cartile dorite in cos (sau verifica ca sunt deja acolo)
3. Deschide cosul: https://www.targulcartii.ro/index.php?route=checkout/cart
4. Click dreapta pe pagina > "View Page Source" (sau Ctrl+U)
5. Ctrl+S si salveaza fisierul HTML in D:\Targul Cartii\
   Numele trebuie sa contina "checkout_cart" si extensia .html
   Exemplu: view-source_checkout_cart.html


PAS 2 - RULEZI PYTHON
----------------------
Deschide terminal/cmd in D:\Targul Cartii\ si ruleaza:

    python cart_manager.py

Sau, daca fisierul HTML are alt nume:

    python cart_manager.py "numele_fisierului.html"

Ce face scriptul:
  - Parseaza HTML-ul cosului salvat
  - Gaseste toate link-urile cartilor
  - Viziteaza fiecare pagina de carte pe targulcartii.ro
  - Extrage product_id-ul din butonul "Adauga in cos"
  - Genereaza hosting/index.html si hosting/script.js
  - Salveaza books.json cu lista completa

Timp estimat: ~1 secunda per carte (250 carti = ~4 minute)

La final arata:
  "GATA! 250 carti | 1234.56 LEI"


PAS 3 - URCI PE HOSTING
------------------------
Urca AMBELE fisiere din folderul hosting\ pe hostingul tau:
  - hosting/index.html
  - hosting/script.js

Trebuie sa fie in ACELASI folder pe hosting.
Exemplu URL final: https://site-ul-tau.ro/cos/index.html


PAS 4 - TRIMITI LINK-UL
------------------------
Trimite-i Andreeei (sau oricui) link-ul catre index.html:
  https://site-ul-tau.ro/cos/index.html


================================================================
  CE FACE ANDREEA (persoana care cumpara)
================================================================

PAS 1 - Deschide link-ul primit
        Vede lista completa de carti, preturi, total estimat

PAS 2 - Apasa butonul rosu COPIAZA SCRIPTUL
        Scriptul se copiaza automat in clipboard

PAS 3 - Deschide https://www.targulcartii.ro/ intr-un tab nou
        Se logheaza in contul ei

PAS 4 - Apasa F12 (deschide Developer Tools)
        Click pe tab-ul "Console"
        Daca Chrome cere, scrie:  allow pasting  si apasa Enter

PAS 5 - Ctrl+V (lipeste scriptul) si apasa Enter
        Apare o bara de progres JOS in pagina
        Cartile se adauga automat (500ms per carte)
        250 carti = ~2 minute

PAS 6 - Cand bara devine verde si scrie "GATA!",
        pagina se redirectioneaza AUTOMAT la cosul de cumparaturi
        Andreea vede toate cartile si apasa "Finalizare comanda"


================================================================
  DETALII TEHNICE
================================================================

Cum functioneaza scriptul JS:
  - Are product_id-urile pre-extrase (nu incarca pagini de carti)
  - Face POST la /index.php?route=checkout/cart/update
    cu product_id=X&quantity=1 pentru fiecare carte
  - Ruleaza pe domeniul targulcartii.ro (necesar pentru sesiune)
  - Bara de progres in partea de jos a paginii
  - Redirect automat la cos dupa finalizare

De ce trebuie F12 + Console:
  Browserul nu permite niciunui site extern sa adauge produse
  in cosul altui site (protectie de securitate "same-origin policy").
  Scriptul TREBUIE sa ruleze pe domeniul targulcartii.ro.
  Singura cale fara extensii de browser este Console.

Cosul expira in 30 minute:
  Dupa ce scriptul adauga cartile, Andreea are 30 de minute
  sa finalizeze comanda. Scriptul ruleaza in ~2 minute,
  deci are ~28 minute sa plateasca.

Link-urile cartilor sunt permanente:
  Chiar daca cosul expira, link-urile catre carti nu expira.
  Poti rerula oricand cart_manager.py cu un cos salvat anterior,
  iar books.json pastreaza lista de carti permanent.


================================================================
  DACA CEVA NU MERGE
================================================================

Problema: "Nu s-a gasit fisierul HTML al cosului"
  Solutie: Pune fisierul HTML in D:\Targul Cartii\
           Numele trebuie sa contina "checkout_cart"

Problema: "SKIP - nu s-a gasit addToCart2"
  Solutie: Cartea poate fi indisponibila (vanduta).
           Verifica link-ul manual in browser.

Problema: Chrome zice "Don't paste code into Console"
  Solutie: Scrie manual:  allow pasting  apoi Enter.
           Abia dupa aceea faci paste cu scriptul.

Problema: Scriptul da erori la adaugare
  Solutie: Verifica ca esti logat pe targulcartii.ro.
           Unele carti pot fi deja vandute = eroare normala.

Problema: Cosul e gol dupa redirect
  Solutie: Nu erai logat. Logheaza-te si reruleaza scriptul.


================================================================
