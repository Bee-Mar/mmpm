import { NgModule } from "@angular/core";
import { TableModule } from "primeng/table";
import { SelectModule } from "primeng/select";
import { MultiSelectModule } from "primeng/multiselect";
import { ButtonModule } from "primeng/button";
import { FormsModule } from "@angular/forms";
import { TabsModule } from "primeng/tabs";
import { DialogModule } from "primeng/dialog";
import { ProgressSpinnerModule } from "primeng/progressspinner";
import { PanelModule } from "primeng/panel";
import { ToolbarModule } from "primeng/toolbar";
import { PopoverModule } from "primeng/popover";
import { DividerModule } from "primeng/divider";
import { ScrollerModule } from "primeng/scroller";
import { TooltipModule } from "primeng/tooltip";
import { InputTextModule } from "primeng/inputtext";
import { ListboxModule } from "primeng/listbox";
import { ScrollPanelModule } from "primeng/scrollpanel";
import { SliderModule } from "primeng/slider";
import { MenuModule } from "primeng/menu";
import { ToastModule } from "primeng/toast";
import { InputNumberModule } from "primeng/inputnumber";
import { AvatarModule } from "primeng/avatar";
import { CardModule } from "primeng/card";
import { SpeedDialModule } from "primeng/speeddial";
import { ConfirmDialogModule } from "primeng/confirmdialog";
import { ToggleButtonModule } from "primeng/togglebutton";

const PrimeNg = [
  TableModule,
  SelectModule,
  MultiSelectModule,
  ButtonModule,
  FormsModule,
  TabsModule,
  DialogModule,
  ProgressSpinnerModule,
  PanelModule,
  ToolbarModule,
  PopoverModule,
  DividerModule,
  ScrollerModule,
  TooltipModule,
  InputTextModule,
  ListboxModule,
  ScrollPanelModule,
  SliderModule,
  InputNumberModule,
  MenuModule,
  ToastModule,
  AvatarModule,
  CardModule,
  SpeedDialModule,
  ConfirmDialogModule,
  ToggleButtonModule,
];

@NgModule({
  declarations: [],
  imports: PrimeNg,
  exports: PrimeNg,
})
export class PrimeNgModule {}
