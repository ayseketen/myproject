import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa genişliği artırıldı
st.set_page_config(layout="wide")


st.title("Personel Takip Paneli")

password = st.text_input("Parola girin", type="password")

if password:
    if password == "ketsan123":
        st.success("Giriş başarılı!")

# Excel dosyasını yükle
        dosya_adi = "sreamlit.xlsx"
        df = pd.read_excel(dosya_adi)



    # Filtreler
        ad_soyad = st.sidebar.multiselect("Ad Soyad", df["OPERATOR_ISIM"].unique())
        bolum = st.sidebar.multiselect("Bölüm", df["BOLUM"].unique())
        tarih_araligi = st.sidebar.date_input(
            "Tarih Aralığı",
            [df["TARIH"].min().date(), df["TARIH"].max().date()]
        )

#####

        filtered_df = df.copy()

#####

        if ad_soyad:
            filtered_df = filtered_df[filtered_df["OPERATOR_ISIM"].isin(ad_soyad)]
        if bolum:
            filtered_df = filtered_df[filtered_df["BOLUM"].isin(bolum)]
        if len(tarih_araligi) == 2:
            start_date, end_date = tarih_araligi
            filtered_df = filtered_df[(filtered_df["TARIH"] >= pd.to_datetime(start_date)) & 
                                        (filtered_df["TARIH"] <= pd.to_datetime(end_date))]
    
#Line chart

        filtered_df["TARIH"] = filtered_df["TARIH"].dt.normalize()

        performans_gunluk = filtered_df.groupby("TARIH")["PERFORMANS"].mean().reset_index
        performans_gunluk = performans_gunluk()
        performans_gunluk["TARIH"] = pd.to_datetime(performans_gunluk["TARIH"])
        performans_gunluk["TARIH_STR"] = performans_gunluk["TARIH"].dt.strftime("%d %B")
        fig = px.line(performans_gunluk, x="TARIH", y= "PERFORMANS", title = "Günlük Performans")
        st.plotly_chart(fig)

# Tablo 1    
        df_grup = filtered_df.groupby("TEZGAHISIM")["URETILENMIKTAR"].sum().reset_index()
        df_grup["URETILENMIKTAR"] = df_grup["URETILENMIKTAR"].round(0).astype(int)
        df_grup.columns = ["Tezgah", "Toplam Üretilen Miktar"]

        
# Tablo 2   
        df_grup2 = filtered_df.groupby("URUN_ADI")["URETILENMIKTAR"].sum().reset_index()
        df_grup2["URETILENMIKTAR"] = df_grup2["URETILENMIKTAR"].round(0).astype(int)
        df_grup2.columns = ["Ürün", "Toplam Üretilen Miktar"]


#Pie chart

        toplam_yapilan = filtered_df.groupby("TEZGAHISIM")["PERFORMANS"].mean().round(2).reset_index()

        fig1 = px.pie(toplam_yapilan, values="PERFORMANS", names="TEZGAHISIM")

        fig1.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="right",
                x=0.8
            )
        )


# urun bazlı bar chart
        performans_ort = filtered_df.groupby(["URUN_KODU", "URUN_ADI"])["PERFORMANS"].mean().round(2).reset_index()

        fig2 = px.bar(
            performans_ort,
            x="URUN_KODU",
            y="PERFORMANS",
            hover_data=["URUN_ADI"],  # Tooltip içine ürün adı
        )
        fig2.update_traces(textposition='outside')


##Yerlesim
        col1, col2 = st.columns(2)  # 2 kolon oluşturduk

        with col1:
            st.subheader("Tezgah Bazında Üretilen Miktar")
            st.dataframe(df_grup)

        with col2:
            
            st.subheader("Ürün Bazında Üretilen Miktar")
            st.dataframe(df_grup2)

        col1, col2 = st.columns(2)  # 2 kolon oluşturduk

        with col1:
            st.markdown("<h3 style='text-align: center;'>Tezgah Bazında Performans</h3>", unsafe_allow_html=True)
            st.plotly_chart(fig1, use_container_width=True)  # use_container_width genişliği kolon genişliğine uyarlar

        with col2:
            st.markdown("### Ürün Bazında Performans")
            st.plotly_chart(fig2, use_container_width=True)


# Boşluk
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# Özet
        st.sidebar.markdown("### GENEL PERFORMANS ÖZETİ")
        if not filtered_df.empty:
            toplam_miktar = filtered_df["URETILENMIKTAR"].sum()
            hedef_toplam = filtered_df["HEDEFMIKTAR"].sum()
            ortalama_perf = filtered_df["PERFORMANS"].mean()
            st.sidebar.write(f"Toplam Üretilen Miktar: {toplam_miktar}")
            st.sidebar.write(f"Hedef Miktar: {hedef_toplam}")
            st.sidebar.write(f"Ortalama Performans: %{ortalama_perf:.2f}")
        else:
            st.sidebar.write("Seçilen filtrelerde veri yok.")

    else:
        st.error("Parola yanlış")


