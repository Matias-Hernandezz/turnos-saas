import type { ComponentType } from "react";
import { Faq } from "@/features/public-site/sections/Faq";
import { Gallery } from "@/features/public-site/sections/Gallery";
import { Hero } from "@/features/public-site/sections/Hero";
import { Location } from "@/features/public-site/sections/Location";
import { Reviews } from "@/features/public-site/sections/Reviews";
import { Services } from "@/features/public-site/sections/Services";
import { Team } from "@/features/public-site/sections/Team";

export const sectionRegistry: Record<string, ComponentType<Record<string, unknown>>> = {
  hero: Hero,
  services: Services,
  team: Team,
  gallery: Gallery,
  reviews: Reviews,
  location: Location,
  faq: Faq,
};
