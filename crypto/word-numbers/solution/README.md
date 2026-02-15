# Word Numbers

## Write-up

This challenge uses a **substitution cipher**: each letter (A–Z) is replaced by the **English word** for the corresponding number (1 = A, 2 = B, …, 26 = Z).

### Steps

1. **Recognize the language**  
   The ciphertext words are in English: *nineteen*, *eight*, *five*, *twelve*, *twenty*, *twenty-one*, etc.

2. **Link words to numbers**  
   Each word denotes a number (1 to 26): *one*=1, *two*=2, …, *nineteen*=19, *twenty*=20, *twenty-one*=21, …, *twenty-six*=26.

3. **Number → letter mapping**  
   Map 1 → A, 2 → B, …, 26 → Z. So *nineteen* (19) → S, *eight* (8) → H, *five* (5) → E, etc.

4. **Decode**  
   By going through the ciphertext word by word (keeping hyphens for compound numbers like *nineteen*, *twenty-one*), you get:  
   `SHELLMATESWORDNUMBERSAREFUN`

5. **Format the flag**  
   The expected format is `shellmates{...}`. In lowercase, with braces:  
   `shellmates{wordnumbersarefun}`

### Possible pitfall

Some numbers are written as a single hyphenated word (*twenty-one*, *eighteen*) or as separate words (*twenty* then *five*). Each token must be handled correctly: for example, do not merge *twenty* and *five* into *twenty-five* (25) when they actually correspond to two letters (T then E).

## Flag

`shellmates{wordnumbersarefun}`
