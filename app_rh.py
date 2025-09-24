import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📊 App RH - Folha de Pagamento", layout="wide")

st.title("📊 App RH - Folha de Pagamento")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue a planilha da folha do RH (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Lê a primeira aba da planilha
    base = pd.read_excel(uploaded_file)

    # Normaliza nomes das colunas (remove espaços, deixa em maiúsculo)
    base.columns = base.columns.str.strip().str.upper()

    # Confere se todas as colunas necessárias existem
    colunas_necessarias = [
        "ORGANOGRAMA",
        "DESCRIÇÃO DO ORGANOGRAMA",
        "EVENTO",
        "DESCRIÇÃO DO EVENTO",
        "P/D/PATRONAL",
        "VÍNCULO",
        "DESCRIÇÃO DO VÍNCULO",
        "VALOR DO EVENTO"
    ]

    for col in colunas_necessarias:
        if col not in base.columns:
            st.error(f"❌ Coluna obrigatória não encontrada na planilha: {col}")
            st.stop()

    # Cria coluna de FONTE DE RECURSO (últimos 8 dígitos do ORGANOGRAMA)
    base["FONTE DE RECURSO"] = base["ORGANOGRAMA"].astype(str).str[-8:]

    # =====================
    # ABA 1 - Vínculo + Organograma + Fonte (Proventos e Descontos)
    # =====================
    aba1_df = (
        base.pivot_table(
            index=["DESCRIÇÃO DO VÍNCULO", "DESCRIÇÃO DO ORGANOGRAMA", "FONTE DE RECURSO"],
            columns="P/D/PATRONAL",
            values="VALOR DO EVENTO",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # =====================
    # ABA 2 - Vínculo + Evento + Fonte
    # =====================
    aba2_df = (
        base.pivot_table(
            index=["DESCRIÇÃO DO VÍNCULO", "DESCRIÇÃO DO EVENTO", "FONTE DE RECURSO"],
            values="VALOR DO EVENTO",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # =====================
    # ABA 3 - Vínculo + Organograma + Fonte (Totais)
    # =====================
    aba3_df = (
        base.pivot_table(
            index=["DESCRIÇÃO DO VÍNCULO", "DESCRIÇÃO DO ORGANOGRAMA", "FONTE DE RECURSO"],
            values="VALOR DO EVENTO",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # =====================
    # ABA 4 - Organograma + Evento + Fonte
    # =====================
    aba4_df = (
        base.pivot_table(
            index=["DESCRIÇÃO DO ORGANOGRAMA", "DESCRIÇÃO DO EVENTO", "FONTE DE RECURSO"],
            values="VALOR DO EVENTO",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # Exibição em abas
    aba1, aba2, aba3, aba4 = st.tabs([
        "📑 Vínculo + Organograma + Fonte",
        "🧾 Vínculo + Evento + Fonte",
        "🏢 Vínculo + Organograma + Fonte (Totais)",
        "📂 Organograma + Evento + Fonte"
    ])

    with aba1:
        st.dataframe(aba1_df, use_container_width=True)

    with aba2:
        st.dataframe(aba2_df, use_container_width=True)

    with aba3:
        st.dataframe(aba3_df, use_container_width=True)

    with aba4:
        st.dataframe(aba4_df, use_container_width=True)

    # =====================
    # Download consolidado em Excel
    # =====================
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        aba1_df.to_excel(writer, sheet_name="Vinculo_Organograma_Fonte", index=False)
        aba2_df.to_excel(writer, sheet_name="Vinculo_Evento_Fonte", index=False)
        aba3_df.to_excel(writer, sheet_name="Totais_Organograma_Fonte", index=False)
        aba4_df.to_excel(writer, sheet_name="Organograma_Evento_Fonte", index=False)

    st.download_button(
        label="📥 Baixar resultado em Excel",
        data=output.getvalue(),
        file_name="resultado_rh.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
