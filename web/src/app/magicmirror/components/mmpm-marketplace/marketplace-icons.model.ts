interface Icon {
  logo: string;
  color: string;
}

export const MarketPlaceIcons: {[key: string]: Icon;} = {
  "Finance": {
    logo: "fa-solid fa-sack-dollar",
    color: "#ffff4d",
  },
  "Sports": {
    logo: "fa-solid fa-baseball-bat-ball",
    color: "#ffff99",
  },
  "Entertainment / Misc": {
    logo: "fa-solid fa-shuffle",
    color: "teal",
  },
  "Education": {
    logo: "fa-solid fa-graduation-cap",
    color: "gray",
  },
  "Utility / IOT / 3rd Party / Integration": {
    logo: "fa-solid fa-wrench",
    color: "gray",
  },
  "Voice Control": {
    logo: "fa-solid fa-microphone",
    color: "#ccff99",
  },
  "Weather": {
    logo: "fa-solid fa-cloud",
    color: "white",
  },
  "News / Information": {
    logo: "fa-solid fa-envelope-open-text",
    color: "#0099ff",
  },
  "Religion": {
    logo: "fa-solid fa-cross",
    color: "#996633",
  },
  "Health": {
    logo: "fa-solid fa-heart",
    color: "red",
  },
  "Transport / Travel": {
    logo: "fa-solid fa-plane",
    color: "#999966",
  },
  "Outdated modules": {
    logo: "fa-solid fa-person-cane",
    color: "#ffff99",
  },
  "Development / Core MagicMirror²": {
    logo: "fa-solid fa-desktop",
    color: "#00cc99",
  },
};

export const DefaultMarketPlaceIcon: Icon = {
  logo: "fa-solid fa-question",
  color: "black"
};
