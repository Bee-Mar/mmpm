import {NgModule} from "@angular/core";
import {TableModule} from "primeng/table";
import {DropdownModule} from "primeng/dropdown";
import {MultiSelectModule} from "primeng/multiselect";
import {ButtonModule} from "primeng/button";
import {FormsModule} from "@angular/forms";
import {TabViewModule} from "primeng/tabview";
import {DialogModule} from "primeng/dialog";
import {ProgressSpinnerModule} from "primeng/progressspinner";
import {PanelModule} from "primeng/panel";
import {ToolbarModule} from "primeng/toolbar";
import {OverlayPanelModule} from "primeng/overlaypanel";
import {DividerModule} from "primeng/divider";
import {ScrollerModule} from "primeng/scroller";
import {TooltipModule} from "primeng/tooltip";
import {InputTextModule} from "primeng/inputtext";
import {ListboxModule} from "primeng/listbox";
import {ScrollPanelModule} from "primeng/scrollpanel";
import {SliderModule} from "primeng/slider";
import {MenuModule} from "primeng/menu";
import {ToastModule} from "primeng/toast";
import {InputNumberModule} from "primeng/inputnumber";
import {AvatarModule} from "primeng/avatar";
import {CardModule} from "primeng/card";
import {SpeedDialModule} from 'primeng/speeddial';
import {ConfirmDialogModule} from 'primeng/confirmdialog';

// all the modules from primeng are grouped in here for cleanliness
const PrimeNg = [
  TableModule,
  DropdownModule,
  MultiSelectModule,
  ButtonModule,
  FormsModule,
  TabViewModule,
  DialogModule,
  ProgressSpinnerModule,
  PanelModule,
  ToolbarModule,
  OverlayPanelModule,
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
];

@NgModule({
  declarations: [],
  imports: PrimeNg,
  exports: PrimeNg,
})
export class PrimeNgModule {}
