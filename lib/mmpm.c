#include "mmpm.h"

char ***allocate_table_memory(const int rows, const int columns) {

  char ***matrix = (char ***)malloc(sizeof(char **) * rows);

  for (int row = 0; row < rows; row++) matrix[row] = (char **)malloc(sizeof(char *) * columns);

  return matrix;
}

void display_table(const char ***modules, const int rows, const int width) {
  ft_table_t *table = ft_create_table();

  ft_set_border_style(table, FT_BOLD2_STYLE);
  ft_set_cell_prop(table, 0, FT_ANY_COLUMN, FT_CPROP_ROW_TYPE, FT_ROW_HEADER);

  for (int i = 0; i < width; i++) {
    ft_set_cell_prop(table, 0, i, FT_CPROP_CONT_FG_COLOR, FT_COLOR_CYAN);
    ft_set_cell_prop(table, 0, i, FT_CPROP_CELL_TEXT_STYLE, FT_TSTYLE_BOLD);
    ft_set_cell_prop(table, 0, i, FT_CPROP_TEXT_ALIGN, FT_ALIGNED_LEFT);
  }

  for (int row = 0; row < rows; row++) ft_row_write_ln(table, width, modules[row]);

  printf("%s\n", ft_to_string(table));
  ft_destroy_table(table);
}
