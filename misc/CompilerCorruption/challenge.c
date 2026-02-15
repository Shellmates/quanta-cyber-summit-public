#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MEM_SHIFT_A 0x33
#define MEM_SHIFT_B 0x22
#define MEM_ROTATE_C 0x11
#define COMPOSITE_KEY (MEM_SHIFT_A ^ MEM_SHIFT_B ^ MEM_ROTATE_C)

void decoy_dump_1(const int* data, int len) {
    printf("[DECOY] 0x");
    for (int i = 0; i < len; i++) {
        printf("%c", data[i] ^ 0x42);
    }
    printf("\n");
}

void decoy_dump_2(const int* data, int len) {
    printf("[NOISE] 0x");
    for (int i = 0; i < len; i++) {
        printf("%c", (data[i] ^ 0x73) + 1);
    }
    printf("\n");
}

void sys_integrity_check(const int* cipher, int len, const char* sector, int phase) {
    int derived_key = COMPOSITE_KEY;
    if (phase == 1) derived_key ^= 0x44;
    if (phase == 2) derived_key ^= 0x33;
    if (phase == 3) derived_key ^= 0x77;
    
    printf("[SECTOR_%s_PHASE_%d]: ", sector, phase);
    for (int i = 0; i < len; i++) {
        printf("%c", cipher[i] ^ derived_key);
    }
    printf("\n");
}

const int DATA_BLOCK_ALPHA[] = {
    0x37, 0x2c, 0x21, 0x28, 0x28, 0x29, 0x25, 0x30, 0x21, 0x37, 0x3f
};

const int DATA_BLOCK_BETA[] = {
    0x50, 0x03, 0x5e, 0x43, 0x02
};

const int DATA_BLOCK_GAMMA[] = {
    0x1b, 0x44, 0x05, 0x28, 0x13
};

const int DATA_BLOCK_DELTA[] = {
    0x77, 0x26, 0x31, 0x23, 0x23
};

const int DATA_BLOCK_EPSILON[] = {
    0x00, 0x41, 0x4e
};

const int DECOY_BLOCK_1[] = {
    0x44, 0x45, 0x43, 0x4f, 0x59, 0x31
};

const int DECOY_BLOCK_2[] = {
    0x46, 0x41, 0x4b, 0x45, 0x32
};

typedef enum {
    TOKEN_EOF = 0, TOKEN_IDENTIFIANT, TOKEN_NOMBRE, TOKEN_HEXADECIMAL,
    TOKEN_STRING, TOKEN_PROTOCOL, TOKEN_ENDPROTOCOL, TOKEN_KEYSPACE,
    TOKEN_MAIN, TOKEN_LOOP, TOKEN_FOR, TOKEN_BYTE, TOKEN_PLAIN,
    TOKEN_CIPHER, TOKEN_HASH, TOKEN_KEY256, TOKEN_PLUS, TOKEN_MINUS,
    TOKEN_MULT, TOKEN_DIV, TOKEN_EQUAL, TOKEN_EQUAL_EQUAL, TOKEN_NOT_EQUAL,
    TOKEN_LESS, TOKEN_GREATER, TOKEN_LESS_EQUAL,
    TOKEN_GREATER_EQUAL, TOKEN_AND, TOKEN_OR,
    TOKEN_ENCRYPT, TOKEN_DECRYPT, TOKEN_HASH_OP,
    TOKEN_DOUBLE_COLON, TOKEN_SEMICOLON, TOKEN_BRACE_OPEN,
    TOKEN_BRACE_CLOSE, TOKEN_PAREN_OPEN, TOKEN_PAREN_CLOSE,
    TOKEN_BRACKET_OPEN, TOKEN_BRACKET_CLOSE, TOKEN_ARROW_RIGHT,
    TOKEN_ARROW_LEFT, TOKEN_COMMENT, TOKEN_ERROR
} TokenType;

typedef struct {
    TokenType type;
    char lexeme[256];
} Token;

char *source_code;
int pos = 0;
int lexical_errors = 0;
int syntax_errors = 0;
int semantic_errors = 0;

Token tokens[1000];
int token_count = 0;

int phase_1_status = 0;
int phase_2_status = 0;
int phase_3_status = 0;

void log_fault() {
    printf("[FAULT_DETECTED]\n");
}

char peek() { return source_code[pos]; }
char peek_next() { return (source_code[pos] == '\0') ? '\0' : source_code[pos + 1]; }
char advance() { return source_code[pos++]; }
void skip_whitespace() { while (isspace(peek())) advance(); }
int is_letter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); }
int is_digit(char c) { return c >= '0' && c <= '9'; }
int is_hex_digit(char c) { return is_digit(c) || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'); }

TokenType check_keyword(const char *lexeme) {
    if (strcmp(lexeme, "protocol") == 0) return TOKEN_PROTOCOL;
    if (strcmp(lexeme, "endprotocol") == 0) return TOKEN_ENDPROTOCOL;
    if (strcmp(lexeme, "keyspace") == 0) return TOKEN_KEYSPACE;
    if (strcmp(lexeme, "main") == 0) return TOKEN_MAIN;
    if (strcmp(lexeme, "loop") == 0) return TOKEN_LOOP;
    if (strcmp(lexeme, "for") == 0) return TOKEN_FOR;
    if (strcmp(lexeme, "byte") == 0) return TOKEN_BYTE;
    if (strcmp(lexeme, "plain") == 0) return TOKEN_PLAIN;
    if (strcmp(lexeme, "cipher") == 0) return TOKEN_CIPHER;
    if (strcmp(lexeme, "hash") == 0) return TOKEN_HASH;
    if (strcmp(lexeme, "key256") == 0) return TOKEN_KEY256;
    return TOKEN_IDENTIFIANT;
}

Token scan_hexadecimal() {
    Token token = {TOKEN_HEXADECIMAL, ""};
    int i = 0;
    token.lexeme[i++] = advance();
    token.lexeme[i++] = advance();
   
    int has_error = 0;
    while (is_hex_digit(peek()) || (!has_error && !isspace(peek()) && peek() != ';' && peek() != '\n')) {
        char c = peek();
        if (!is_hex_digit(c) && !isspace(c) && c != ';' && c != '\n') {
            has_error = 1;
            lexical_errors++;
        }
        token.lexeme[i++] = advance();
    }
   
    token.lexeme[i] = '\0';
    if (has_error) {
        token.type = TOKEN_ERROR;
        log_fault();
    }
    return token;
}

Token scan_number() {
    Token token = {TOKEN_NOMBRE, ""};
    int i = 0;
    while (is_digit(peek())) token.lexeme[i++] = advance();
    token.lexeme[i] = '\0';
    return token;
}

Token scan_identifier() {
    Token token = {TOKEN_IDENTIFIANT, ""};
    int i = 0;
    if (is_letter(peek()) || peek() == '_') token.lexeme[i++] = advance();
    while (is_letter(peek()) || is_digit(peek()) || peek() == '_')
        token.lexeme[i++] = advance();
    token.lexeme[i] = '\0';
    token.type = check_keyword(token.lexeme);
    return token;
}

Token scan_string() {
    Token token = {TOKEN_ERROR, ""};
    int i = 0;
    token.lexeme[i++] = advance();
   
    while (peek() != '"' && peek() != '\0' && peek() != '\n') {
        if (i < 255) token.lexeme[i++] = advance();
        else advance();
    }
   
    if (peek() == '"') {
        token.lexeme[i++] = advance();
        token.lexeme[i] = '\0';
        token.type = TOKEN_STRING;
    } else {
        log_fault();
        token.type = TOKEN_ERROR;
        lexical_errors++;
    }
    return token;
}

Token scan_comment() {
    Token token = {TOKEN_COMMENT, "//..."};
    advance(); advance();
    while (peek() != '\n' && peek() != '\0') advance();
    return token;
}

Token get_next_token() {
    skip_whitespace();
    Token token = {TOKEN_ERROR, ""};
    char c = peek();
   
    if (c == '\0') { token.type = TOKEN_EOF; strcpy(token.lexeme, "EOF"); return token; }
    if (c == '/' && peek_next() == '/') return scan_comment();
    if (c == '0' && (peek_next() == 'x' || peek_next() == 'X')) return scan_hexadecimal();
    if (is_digit(c)) return scan_number();
    if (c == '"') return scan_string();
    if (is_letter(c) || c == '_') return scan_identifier();
   
    token.lexeme[0] = advance();
    token.lexeme[1] = '\0';
   
    switch (token.lexeme[0]) {
        case '@':
            if (peek() == '>') { advance(); token.type = TOKEN_ENCRYPT; strcpy(token.lexeme, "@>"); }
            else if (is_letter(peek()) || peek() == '_') {
                Token id = scan_identifier();
                id.type = check_keyword(id.lexeme);
                token.lexeme[0] = '@';
                strncpy(token.lexeme + 1, id.lexeme, sizeof(token.lexeme) - 2);
                token.type = id.type;
                return token;
            }
            break;
        case '<': if (peek() == '@') { advance(); token.type = TOKEN_DECRYPT; }
            else if (peek() == '=') { advance(); token.type = TOKEN_LESS_EQUAL; }
            else if (peek() == '-') { advance(); token.type = TOKEN_ARROW_LEFT; }
            else token.type = TOKEN_LESS; break;
        case '>': if (peek() == '=') { advance(); token.type = TOKEN_GREATER_EQUAL; }
            else token.type = TOKEN_GREATER; break;
        case '#': if (peek() == '>') { advance(); token.type = TOKEN_HASH_OP; } break;
        case '&': if (peek() == '&') { advance(); token.type = TOKEN_AND; } break;
        case '|': if (peek() == '|') { advance(); token.type = TOKEN_OR; } break;
        case '!': if (peek() == '=') { advance(); token.type = TOKEN_NOT_EQUAL; } break;
        case '=': if (peek() == '=') { advance(); token.type = TOKEN_EQUAL_EQUAL; }
            else token.type = TOKEN_EQUAL; break;
        case '-': if (peek() == '>') { advance(); token.type = TOKEN_ARROW_RIGHT; }
            else token.type = TOKEN_MINUS; break;
        case ':': if (peek() == ':') { advance(); token.type = TOKEN_DOUBLE_COLON; } break;
        case '+': token.type = TOKEN_PLUS; break;
        case '*': token.type = TOKEN_MULT; break;
        case '/': token.type = TOKEN_DIV; break;
        case ';': token.type = TOKEN_SEMICOLON; break;
        case '{': token.type = TOKEN_BRACE_OPEN; break;
        case '}': token.type = TOKEN_BRACE_CLOSE; break;
        case '(': token.type = TOKEN_PAREN_OPEN; break;
        case ')': token.type = TOKEN_PAREN_CLOSE; break;
        case '[': token.type = TOKEN_BRACKET_OPEN; break;
        case ']': token.type = TOKEN_BRACKET_CLOSE; break;
    }
    return token;
}

void tokenize(const char* code) {
    source_code = (char*)code;
    pos = 0;
    token_count = 0;
   
    Token token;
    do {
        token = get_next_token();
        if (token.type != TOKEN_COMMENT && token.type != TOKEN_ERROR) {
            tokens[token_count++] = token;
        }
    } while (token.type != TOKEN_EOF && token_count < 1000);
}

typedef struct { char name[256]; char type[50]; } Symbol;
Symbol symbol_table[100];
int symbol_count = 0;

void add_symbol(const char* name, const char* type) {
    for (int i = 0; i < symbol_count; i++) {
        if (strcmp(symbol_table[i].name, name) == 0) {
            log_fault();
            semantic_errors++; return;
        }
    }
    strcpy(symbol_table[symbol_count].name, name);
    strcpy(symbol_table[symbol_count].type, type);
    symbol_count++;
}

char* get_type(const char* name) {
    for (int i = 0; i < symbol_count; i++) {
        if (strcmp(symbol_table[i].name, name) == 0) return symbol_table[i].type;
    }
    log_fault();
    semantic_errors++;
    return "error";
}

int types_compatible(const char* t1, const char* t2) {
    if (strcmp(t1, "error") == 0 || strcmp(t2, "error") == 0) return 1;
    return strcmp(t1, t2) == 0;
}

int token_index = 0;
Token current_token;

void advance_token() {
    if (token_index < token_count - 1) current_token = tokens[++token_index];
}

int check_token(TokenType type) { return current_token.type == type; }

void expect_token(TokenType type) {
    if (!check_token(type)) {
        log_fault();
        syntax_errors++;
    } else advance_token();
}

typedef struct { char type[50]; } ExpressionInfo;
ExpressionInfo parse_expression();

ExpressionInfo parse_factor() {
    ExpressionInfo info = {""};
    if (check_token(TOKEN_NOMBRE)) { strcpy(info.type, "byte"); advance_token(); }
    else if (check_token(TOKEN_HEXADECIMAL)) { strcpy(info.type, "key256"); advance_token(); }
    else if (check_token(TOKEN_STRING)) { strcpy(info.type, "plain"); advance_token(); }
    else if (check_token(TOKEN_IDENTIFIANT)) { strcpy(info.type, get_type(current_token.lexeme)); advance_token(); }
    else if (check_token(TOKEN_PAREN_OPEN)) { advance_token(); info = parse_expression(); expect_token(TOKEN_PAREN_CLOSE); }
    return info;
}

ExpressionInfo parse_term() {
    ExpressionInfo left = parse_factor();
    while (check_token(TOKEN_MULT) || check_token(TOKEN_DIV)) {
        advance_token(); parse_factor(); strcpy(left.type, "byte");
    }
    return left;
}

ExpressionInfo parse_arithmetic() {
    ExpressionInfo left = parse_term();
    while (check_token(TOKEN_PLUS) || check_token(TOKEN_MINUS)) {
        advance_token(); parse_term(); strcpy(left.type, "byte");
    }
    return left;
}

ExpressionInfo parse_expression() {
    ExpressionInfo left = parse_arithmetic();
    if (check_token(TOKEN_ENCRYPT)) {
        advance_token(); parse_arithmetic(); strcpy(left.type, "cipher");
    } else if (check_token(TOKEN_HASH_OP)) {
        advance_token(); strcpy(left.type, "hash");
    }
    if (check_token(TOKEN_LESS) || check_token(TOKEN_GREATER) || check_token(TOKEN_EQUAL_EQUAL)) {
        advance_token(); parse_arithmetic(); strcpy(left.type, "byte");
    }
    return left;
}

void parse_statement() {
    if (check_token(TOKEN_BYTE) || check_token(TOKEN_PLAIN) ||
        check_token(TOKEN_CIPHER) || check_token(TOKEN_HASH) || check_token(TOKEN_KEY256)) {
        char var_type[50]; strcpy(var_type, current_token.lexeme); advance_token();
        if (check_token(TOKEN_DOUBLE_COLON)) {
            advance_token();
            if (check_token(TOKEN_IDENTIFIANT)) {
                char var_name[256]; strcpy(var_name, current_token.lexeme); advance_token();
                add_symbol(var_name, var_type);
                if (check_token(TOKEN_EQUAL)) {
                    advance_token(); ExpressionInfo expr = parse_expression();
                    if (!types_compatible(var_type, expr.type)) {
                        log_fault();
                        semantic_errors++;
                    }
                }
            }
            expect_token(TOKEN_SEMICOLON);
        }
    }
    else if (check_token(TOKEN_IDENTIFIANT)) {
        char var_name[256]; strcpy(var_name, current_token.lexeme);
        char* var_type = get_type(var_name); advance_token();
        expect_token(TOKEN_EQUAL);
        ExpressionInfo expr = parse_expression();
        if (!types_compatible(var_type, expr.type)) {
            log_fault();
            semantic_errors++;
        }
        expect_token(TOKEN_SEMICOLON);
    }
    else if (check_token(TOKEN_ARROW_RIGHT)) { advance_token(); parse_expression(); expect_token(TOKEN_SEMICOLON); }
    else if (check_token(TOKEN_ARROW_LEFT)) {
        advance_token();
        if(check_token(TOKEN_IDENTIFIANT)) { get_type(current_token.lexeme); advance_token(); }
        expect_token(TOKEN_SEMICOLON);
    }
    else if (check_token(TOKEN_LOOP)) {
        advance_token(); expect_token(TOKEN_BRACKET_OPEN); parse_expression();
        expect_token(TOKEN_BRACKET_CLOSE); expect_token(TOKEN_BRACE_OPEN);
        while (!check_token(TOKEN_BRACE_CLOSE) && !check_token(TOKEN_EOF)) parse_statement();
        expect_token(TOKEN_BRACE_CLOSE);
    } else advance_token();
}

void parse_program() {
    expect_token(TOKEN_PROTOCOL); expect_token(TOKEN_IDENTIFIANT);
    if (check_token(TOKEN_KEYSPACE)) {
        advance_token(); expect_token(TOKEN_BRACE_OPEN);
        while (!check_token(TOKEN_BRACE_CLOSE) && !check_token(TOKEN_EOF)) parse_statement();
        expect_token(TOKEN_BRACE_CLOSE);
    }
    expect_token(TOKEN_MAIN); expect_token(TOKEN_BRACE_OPEN);
    while (!check_token(TOKEN_BRACE_CLOSE) && !check_token(TOKEN_EOF)) parse_statement();
    expect_token(TOKEN_BRACE_CLOSE); expect_token(TOKEN_ENDPROTOCOL);
}

int main() {
    
    printf("[INFO] Loading memory segments...\n");
    printf("[INFO] Initializing phase controllers...\n");
    printf("[INFO] Composite key: 0x%02X\n\n", COMPOSITE_KEY);
    
    const char* code_source =
        "@protocol SecureVault\n"
        "\n"
        "@keyspace {\n"
        "    key256 :: master_key = 0x41424344454647484950Z;\n"
        "    byte :: iterations = 256;\n"
        "    plain :: seed = \"initialization_vector\";\n"
        "}\n"
        "\n"
        "@main {\n"
        "    plain :: payload = \"SecureData\"\n"
        "    \n"
        "    cipher :: encrypted = master_key @> payload;\n"
        "    \n"
        "    byte :: counter = iterations;\n"
        "    @loop [ counter > 0 ] {\n"
        "        counter = counter - 1;\n"
        "        encrypted = encrypted @> seed;\n"
        "    }\n"
        "    \n"
        "    hash :: digest = payload #>;\n"
        "    -> digest;\n"
        "}\n"
        "\n"
        "@endprotocol";
    
    printf("[PHASE 1] Lexical Analysis...\n");
    tokenize(code_source);
    if (lexical_errors > 0) {
        printf("[CRITICAL] Phase 1 integrity check FAILED (code: 0xLEX)\n");
    
        printf("[STATUS] Aborting analysis sequence\n\n");
        return 1;
    }
    phase_1_status = 1;
    printf("[SUCCESS] Phase 1 integrity verified\n");
    sys_integrity_check(DATA_BLOCK_ALPHA, sizeof(DATA_BLOCK_ALPHA)/sizeof(int), "A1", 1);
    decoy_dump_1(DECOY_BLOCK_1, sizeof(DECOY_BLOCK_1)/sizeof(int));
    printf("\n");

    printf("[PHASE 2] Syntax Analysis...\n");
    token_index = 0; current_token = tokens[0];
    parse_program();
    if (syntax_errors > 0) {
        printf("[CRITICAL] Phase 2 integrity check FAILED (code: 0xSYN)\n");
      
        printf("[STATUS] Aborting analysis sequence\n\n");
        return 1;
    }
    phase_2_status = 1;
    printf("[SUCCESS] Phase 2 integrity verified\n");
    sys_integrity_check(DATA_BLOCK_BETA, sizeof(DATA_BLOCK_BETA)/sizeof(int), "B2", 2);
    sys_integrity_check(DATA_BLOCK_GAMMA, sizeof(DATA_BLOCK_GAMMA)/sizeof(int), "C3", 3);
    decoy_dump_2(DECOY_BLOCK_2, sizeof(DECOY_BLOCK_2)/sizeof(int));
    printf("\n");

    printf("[PHASE 3] Semantic Analysis...\n");
    if (semantic_errors > 0) {
        printf("[CRITICAL] Phase 3 integrity check FAILED (code: 0xSEM)\n");
     
        printf("[STATUS] Aborting analysis sequence\n\n");
        return 1;
    }
    phase_3_status = 1;
    printf("[SUCCESS] Phase 3 integrity verified\n");
    sys_integrity_check(DATA_BLOCK_DELTA, sizeof(DATA_BLOCK_DELTA)/sizeof(int), "D4", 1);
    sys_integrity_check(DATA_BLOCK_EPSILON, sizeof(DATA_BLOCK_EPSILON)/sizeof(int), "E5", 2);
    printf("\n");
    
    if (phase_1_status && phase_2_status && phase_3_status) {
        printf("[SYSTEM] All integrity checks passed\n");
        printf("[STATUS] Protocol analysis complete\n");
        printf("[INFO] Data segments unlocked in sectors:\n");
        printf("        A1, B2, C3, D4, E5\n");
    }
    
    return 0;
}
