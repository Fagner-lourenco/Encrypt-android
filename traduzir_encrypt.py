#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import xml.dom.minidom as minidom
from pathlib import Path
import argparse

def substituir_texto_preservando_tags(arquivo, modo_simulacao=False):
    """Processa um arquivo XML de strings, preservando os nomes das tags."""
    try:
        # Verificar se o arquivo existe
        if not os.path.isfile(arquivo):
            print(f"Arquivo não encontrado: {arquivo}")
            return False

        # Parse do XML usando minidom - convertendo para string para evitar erro
        dom = minidom.parse(str(arquivo))
        root = dom.documentElement
        modificado = False

        # Substituições a serem feitas apenas nos valores de texto
        substituicoes = [
            ("Signal", "Encrypt"),
            ("Molly", "Encrypt"),
            ("signal.org", "encrypt.tech"),
            ("molly.im", "encrypt.tech")
        ]
        
        # Função para substituir texto preservando case
        def substituir_texto_preservando_case(texto):
            if not texto:
                return texto
                
            for antigo, novo in substituicoes:
                # Substituição case-insensitive com preservação do case
                pattern = re.compile(re.escape(antigo), re.IGNORECASE)
                matches = list(pattern.finditer(texto))
                
                # Substitui de trás para frente para não afetar índices
                for m in reversed(matches):
                    inicio, fim = m.span()
                    palavra_original = texto[inicio:fim]
                    
                    # Decide como preservar o case
                    if palavra_original.isupper():
                        substituicao = novo.upper()
                    elif palavra_original[0].isupper() and palavra_original[1:].islower():
                        substituicao = novo[0].upper() + novo[1:].lower()
                    else:
                        substituicao = novo
                        
                    texto = texto[:inicio] + substituicao + texto[fim:]
            
            return texto

        # Processa elementos <string>
        for string_elem in root.getElementsByTagName("string"):
            # Ignora strings vazias
            if not string_elem.childNodes or not string_elem.childNodes[0].nodeValue:
                continue
                
            # Obtém o texto atual
            texto_original = string_elem.childNodes[0].nodeValue
            texto_novo = substituir_texto_preservando_case(texto_original)
            
            # Se houve modificação, atualiza
            if texto_original != texto_novo:
                string_elem.childNodes[0].nodeValue = texto_novo
                modificado = True
                
        # Processa elementos <plurals>
        for plurals in root.getElementsByTagName("plurals"):
            for item in plurals.getElementsByTagName("item"):
                # Ignora items vazios
                if not item.childNodes or not item.childNodes[0].nodeValue:
                    continue
                
                # Obtém o texto atual
                texto_original = item.childNodes[0].nodeValue
                texto_novo = substituir_texto_preservando_case(texto_original)
                
                # Se houve modificação, atualiza
                if texto_original != texto_novo:
                    item.childNodes[0].nodeValue = texto_novo
                    modificado = True
                    
        # Se houve modificação e não estamos em modo simulação, salva o arquivo
        if modificado and not modo_simulacao:
            with open(str(arquivo), 'w', encoding='utf-8') as f:
                # Usa a função toxml com encoding explícito e preservando a declaração XML
                xml_text = dom.toxml(encoding='utf-8').decode('utf-8')
                f.write(xml_text)
            print(f"✅ Alterado: {arquivo}")
        elif modificado:
            print(f"🔍 Simulação: Alterações necessárias em {arquivo}")
        else:
            print(f"⏭️ Sem alterações necessárias: {arquivo}")
            
        return modificado
            
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo}: {e}")
        return False

def verificar_strings_nao_traduzidas(arquivo):
    """Verifica strings que ainda contêm termos não substituídos."""
    termos_para_verificar = ["Signal", "Molly", "signal.org", "molly.im"]
    strings_problematicas = []
    
    try:
        # Verificar se o arquivo existe
        if not os.path.isfile(arquivo):
            print(f"Arquivo não encontrado: {arquivo}")
            return []

        # Parse do XML - convertendo para string para evitar erro
        dom = minidom.parse(str(arquivo))
        root = dom.documentElement
        
        # Verifica todas as strings
        for string_elem in root.getElementsByTagName("string"):
            if string_elem.childNodes and string_elem.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
                texto = string_elem.childNodes[0].nodeValue
                if texto:
                    for termo in termos_para_verificar:
                        if re.search(termo, texto, re.IGNORECASE):
                            nome = string_elem.getAttribute('name')
                            strings_problematicas.append((nome or 'sem-nome', texto))
                            break
        
        # Verifica plurais também
        for plurals in root.getElementsByTagName("plurals"):
            nome = plurals.getAttribute('name') or 'sem-nome'
            for item in plurals.getElementsByTagName("item"):
                if item.childNodes and item.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
                    texto = item.childNodes[0].nodeValue
                    if texto:
                        for termo in termos_para_verificar:
                            if re.search(termo, texto, re.IGNORECASE):
                                quantidade = item.getAttribute('quantity') or 'desconhecido'
                                strings_problematicas.append((f"{nome}[{quantidade}]", texto))
                                break
        
        return strings_problematicas
    except Exception as e:
        print(f"❌ Erro ao verificar {arquivo}: {e}")
        return []

def main():
    # Configurar argumentos
    parser = argparse.ArgumentParser(description='Script para traduzir e verificar arquivos XML do Encrypt-android')
    parser.add_argument('--modo', choices=['substituir', 'verificar'], default='substituir', 
                        help='Modo de operação: substituir termos ou verificar não traduzidos')
    parser.add_argument('--caminho', default='.', 
                        help='Caminho raiz do projeto (padrão: diretório atual)')
    parser.add_argument('--simular', action='store_true', 
                        help='Modo de simulação: não faz alterações reais nos arquivos')
    parser.add_argument('--reverter', action='store_true',
                        help='Reverte alterações feitas em nomes de tags (corrige erros anteriores)')
    
    args = parser.parse_args()
    
    # Pasta raiz do projeto
    pasta_raiz = Path(args.caminho)
    pasta_res = pasta_raiz / "app" / "src" / "main" / "res"
    
    if not pasta_res.exists():
        print(f"⚠️ Diretório de recursos não encontrado: {pasta_res}")
        # Tente encontrar o diretório res na raiz atual
        pasta_res = pasta_raiz / "res"
        if not pasta_res.exists():
            print(f"❌ Diretório de recursos não encontrado: {pasta_res}")
            return
        else:
            print(f"✅ Usando diretório de recursos alternativo: {pasta_res}")
    
    # Conta arquivos processados e substituições feitas
    arquivos_processados = 0
    arquivos_alterados = 0
    strings_problematicas_total = 0
    
    # Processa todos os arquivos strings.xml e strings2.xml nas pastas values-*
    for pasta in pasta_res.glob("values*"):
        # Removida a condição que ignora pastas values-v21, etc.
        # Agora todas as pastas que começam com "values" serão processadas
            
        # Processa strings.xml
        arquivo_strings = pasta / "strings.xml"
        if arquivo_strings.exists():
            arquivos_processados += 1
            
            if args.modo == 'substituir':
                if substituir_texto_preservando_tags(arquivo_strings, args.simular):
                    arquivos_alterados += 1
            
            elif args.modo == 'verificar':
                strings_problematicas = verificar_strings_nao_traduzidas(arquivo_strings)
                if strings_problematicas:
                    print(f"\n📋 Arquivo: {arquivo_strings}")
                    for nome, texto in strings_problematicas:
                        print(f"  - {nome}: \"{texto}\"")
                    strings_problematicas_total += len(strings_problematicas)
        
        # Processa strings2.xml
        arquivo_strings2 = pasta / "strings2.xml"
        if arquivo_strings2.exists():
            arquivos_processados += 1
            
            if args.modo == 'substituir':
                if substituir_texto_preservando_tags(arquivo_strings2, args.simular):
                    arquivos_alterados += 1
            
            elif args.modo == 'verificar':
                strings_problematicas = verificar_strings_nao_traduzidas(arquivo_strings2)
                if strings_problematicas:
                    print(f"\n📋 Arquivo: {arquivo_strings2}")
                    for nome, texto in strings_problematicas:
                        print(f"  - {nome}: \"{texto}\"")
                    strings_problematicas_total += len(strings_problematicas)
    
    # Exibe resumo
    print("\n=== 📊 Resumo ===")
    print(f"Total de arquivos processados: {arquivos_processados}")
    
    if args.modo == 'substituir':
        if args.simular:
            print(f"Total de arquivos que seriam alterados: {arquivos_alterados}")
            print("Nenhuma alteração foi feita (modo de simulação)")
        else:
            print(f"Total de arquivos alterados: {arquivos_alterados}")
    elif args.modo == 'verificar':
        print(f"Total de strings não traduzidas: {strings_problematicas_total}")
        if strings_problematicas_total > 0:
            print("\nPara corrigir estas strings não traduzidas, execute o script no modo 'substituir':")
            print("python traduzir_encrypt.py --modo substituir")

if __name__ == "__main__":
    main()