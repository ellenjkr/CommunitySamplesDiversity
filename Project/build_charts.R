library(conflicted)
conflict_prefer("filter", "dplyr")
conflict_prefer("lag", "dplyr")
library(tidyverse)
library(dplyr)
library(RColorBrewer)
library(ggplot2)

margin_spacer <- function(x) {
  # where x is the column in your dataset
  left_length <- nchar(levels(factor(x)))[1]
  if (left_length > 8) {
    return((left_length - 8) * 4)
  }
  else
    return(0)
}


# Função phylum_chart
phylum_chart <- function(file) {
  df <- read.table(file, header = TRUE, sep = '\t')
  df <- df %>%
  group_by(Filo) %>%
  summarise(across(where(is.numeric), sum)) %>%
  ungroup()

  # Normalizando os valores como porcentagem
  df <- df %>%
    mutate(across(where(is.numeric), ~ (. / sum(.)) * 100))


  library(ggplot2)

  print(df)
  # Convertendo o dataframe em formato longo
  df_long <- tidyr::gather(df, Amostra, Valor, -Filo)
  print(df_long)
  df_final <- df_long %>%
  group_by(Amostra) %>%
  arrange(desc(Valor)) %>%
  mutate(rank = row_number()) %>%
  mutate(Filo = ifelse(rank <= 5, Filo, "Outros")) %>%
  ungroup() %>%
  select(-rank)


  num_uniques <- df_final %>% 
    distinct(Filo) %>% 
    nrow()

  getPalette = colorRampPalette(brewer.pal(9, "Set1"))

  # Criando o gráfico de barras empilhadas
  p <- ggplot(df_final, aes(x = Amostra, y = Valor, fill = Filo)) +
    geom_bar(stat = "identity", position = "stack", width = 0.8) +  # Ajuste a largura aqui
    labs(title = "Ocorrências - Filo",
         x = "Amostra",
         y = "%") +
    scale_y_continuous(breaks = seq(0, 100, by = 10)) + 
    scale_fill_manual(values=getPalette(num_uniques)) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1),
      plot.margin = margin(l = 0 + margin_spacer(df_final$Amostra), t = 15)
    )

  # Salvando o gráfico com uma largura maior (por exemplo, 12 polegadas)
  ggsave("amostras.jpg", device='jpg', plot = p, width = 12, height = 6)
  
}

test <- function(file) {
  df <- read.table(file, header = TRUE, sep = '\t')
  df <- df %>%
  group_by(Filo) %>%
  summarise(across(where(is.numeric), sum)) %>%
  ungroup()

  # Normalizando os valores como porcentagem
  df <- df %>%
    mutate(across(where(is.numeric), ~ (. / sum(.)) * 100))

  # Convertendo o dataframe em formato longo
  df <- tidyr::gather(df, Amostra, Valor, -Filo)

  print(df)

  df_final <- df %>%
  group_by(Amostra) %>%
  arrange(desc(Valor)) %>%
  mutate(rank = row_number()) %>%
  mutate(Filo = ifelse(rank <= 5, Filo, "Outros")) %>%
  ungroup() %>%
  select(-rank)

  print(df_final, n=40)


  num_uniques <- df_final %>% 
    distinct(Filo) %>% 
    nrow()

  getPalette = colorRampPalette(brewer.pal(9, "Set1"))

  p <- ggplot(df_final, aes(x = Amostra, y = Valor, fill = Filo)) +
  geom_bar(stat = "identity") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(x = "Amostra", y = "Valor", fill = "Filo") +
  scale_fill_manual(values=getPalette(num_uniques)) +
  ggtitle("Gráfico de Barras Empilhadas")

  ggsave("test.jpg", device='jpg', plot = p, width = 12, height = 6)


}
# Função meta_charts
meta_charts <- function(file, meta_file) {
  samples_df <- read.table(file, header = TRUE, sep = '\t', check.names = FALSE)
  samples_df <- samples_df %>%
  group_by(Filo) %>%
  summarise(across(where(is.numeric), sum)) %>%
  ungroup()
  
  meta <- read.table(meta_file, header = TRUE, sep = '\t')
  
  df_values_melted <- samples_df %>% pivot_longer(cols = -Filo, names_to = "sample", values_to = "valor")
  df_merged <- inner_join(df_values_melted, meta, by = "sample")

  for (category in colnames(meta)[-1]) {
    df <- df_merged %>%
    pivot_wider(names_from = category, values_from = valor, values_fill = 0)

    unique_values <- unique(df_merged[, category, drop = FALSE])
    unique_values <- pull(unique_values, category)
    selected_columns <- append(unique_values, 'Filo')
    df <- df[, selected_columns]


    df <- df %>%
    group_by(Filo) %>%
    summarise_all(.funs = sum)

    df <- df %>%
    mutate(across(where(is.numeric), ~ (. / sum(.)) * 100))

    df_long <- tidyr::gather(df, Category, Valor, -Filo)
    df_final <- df_long %>%
    group_by(Category) %>%
    arrange(desc(Valor)) %>%
    mutate(rank = row_number()) %>%
    mutate(Filo = ifelse(rank <= 5, Filo, "Outros")) %>%
    ungroup() %>%
    select(-rank)

    num_uniques <- df_final %>% 
    distinct(Filo) %>% 
    nrow()

    getPalette = colorRampPalette(brewer.pal(9, "Set1"))

    # Criando o gráfico de barras empilhadas
    p <- ggplot(df_final, aes(x = Category, y = Valor, fill = Filo)) +
      geom_bar(stat = "identity", position = "stack", width = 0.8) +  # Ajuste a largura aqui
      labs(title = "Ocorrências - Filo",
           x = category,
           y = "%") +
      scale_y_continuous(breaks = seq(0, 100, by = 10)) + 
      scale_fill_manual(values=getPalette(num_uniques)) +
      theme_minimal() +
      theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        plot.margin = margin(l = 15, t = 15, b = 15, r = 15)
      )

    nome_arquivo <- paste(category, ".jpg", sep = "")

    # Salvando o gráfico com uma largura maior (por exemplo, 12 polegadas)
    ggsave(nome_arquivo, device='jpg', plot = p, width = 12, height = 6)

  }  
}


# Executar as funções
phylum_chart('lib3_stamp.tsv')
meta_charts('lib3_stamp.tsv', 'meta_v5.tsv')

# test('lib3_stamp.tsv')