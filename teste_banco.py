from banco import salvar_sugestao, listar_sugestoes, registrar_aposta, salvar_resultado_sorteio, conferir_apostas

# 1️⃣ Criar e salvar uma sugestão de aposta
print("\n🔹 Salvando sugestão de aposta...")
salvar_sugestao([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

# 2️⃣ Listar todas as sugestões registradas
print("\n🔹 Listando sugestões registradas...")
sugestoes = listar_sugestoes()
print(sugestoes)

# Pegamos o ID da primeira sugestão para registrar a aposta
id_sugestao = sugestoes[0][0] if sugestoes else None

# 3️⃣ Registrar aposta realizada no sorteio 3000
if id_sugestao:
    print(f"\n🔹 Registrando aposta realizada (ID: {id_sugestao}) para o sorteio 3000...")
    registrar_aposta(id_sugestao=id_sugestao, sorteio=3001)
else:
    print("\n⚠️ Nenhuma sugestão encontrada para registrar aposta!")

# 4️⃣ Salvar resultado do sorteio 3000
print("\n🔹 Salvando resultado do sorteio 3000...")
salvar_resultado_sorteio(3001, [1,3,5,7,9,10,12,14,15,18,19,21,22,24,25])

# 5️⃣ Conferir apostas realizadas no sorteio 3000
print("\n🔹 Conferindo apostas realizadas no sorteio 3000...")
resultado_apostas = conferir_apostas(3001)
print(resultado_apostas)

# Finalizando testes
print("\n✅ Teste do banco concluído com sucesso!")