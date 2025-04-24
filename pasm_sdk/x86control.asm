.text
.global _start

_start:
    mov r0, #0
    mov r1, #msg
    mov r2, #13
    mov r7, #4
    svc #0

    mov r3, #100
loop:
    sub r3, r3, #1
    cmp r3, #0
    bgt loop

    mov r4, #10
    mov r5, #5
    mul r6, r4, r5
    cmp r6, #50
    bne fail

    push {r4, r5, r6}
    ldr r7, [sp]
    str r7, [r1]
    pop {r4, r5, r6}

    bl call_me
    b done

fail:
    mov r0, #1
    mov r7, #1
    svc #0

call_me:
    mov r0, #42
    bx lr

done:
    mov r0, #0
    mov r7, #1
    svc #0


    mov r0, #1
    mov r1, #2
    add r2, r0, r1
    sub r2, r2, #1
    cmp r2, #2
    bne skip1
    mov r3, #3
skip1:
    mov r4, #4
    add r5, r4, r1
    sub r6, r5, r3
    cmp r6, #1
    bgt skip2
    mov r7, #7
skip2:
    push {r0, r1}
    pop {r0, r1}
    bx lr

    mov r0, #8
    mov r1, #9
    add r2, r0, r1
    sub r2, r2, #2
    cmp r2, #10
    bne skip3
    mov r3, #11
skip3:
    mov r4, #12
    add r5, r4, r1
    sub r6, r5, r3
    cmp r6, #3
    bgt skip4
    mov r7, #14
skip4:
    push {r0, r1}
    pop {r0, r1}
    bx lr


    mov r0, #16
    mov r1, #17
    add r2, r0, r1
    sub r2, r2, #4
    cmp r2, #29
    bne skip5
    mov r3, #18
skip5:
    mov r4, #19
    add r5, r4, r1
    sub r6, r5, r3
    cmp r6, #1
    bgt skip6
    mov r7, #21
skip6:
    push {r0, r1}
    pop {r0, r1}
    bx lr


    mov r3, #20
loop2:
    sub r3, r3, #1
    cmp r3, #0
    bgt loop2

    mov r3, #20
loop3:
    sub r3, r3, #1
    cmp r3, #0
    bgt loop3


.rept 40
    mov r0, #0
    add r1, r0, #1
    sub r2, r1, #1
    cmp r2, #0
    bne loop
.endr

.data
msg:    .asciz "Hello, ARM!"
value:  .word 0x12345678
        .half 0xABCD
        .byte 0x42
        .ascii "DATA"
        .space 8
