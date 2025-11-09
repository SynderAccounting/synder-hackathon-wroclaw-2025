import { sql } from "drizzle-orm";
import { pgTable, text, varchar, jsonb, boolean, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const platforms = pgTable("platforms", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  type: text("type").notNull(),
  name: text("name").notNull(),
  credentials: jsonb("credentials").notNull(),
});

const shopifyCredentialsSchema = z.object({
  api_key: z.string().min(1, "API key is required"),
  api_version: z.string().min(1, "API version is required"),
});

const squareCredentialsSchema = z.object({
  environment: z.enum(["sandbox", "production"]),
  access_token: z.string().min(1, "Access token is required"),
  application_id: z.string().min(1, "Application ID is required"),
  location_id: z.string().optional(),
});

const credentialsSchema = z.union([shopifyCredentialsSchema, squareCredentialsSchema]);

export const insertPlatformSchema = createInsertSchema(platforms).omit({
  id: true,
}).extend({
  credentials: credentialsSchema,
});

export type InsertPlatform = z.infer<typeof insertPlatformSchema>;
export type Platform = typeof platforms.$inferSelect;

export interface PlatformPublic {
  id: string;
  type: string;
  name: string;
  hasCredentials: boolean;
  settings: PlatformSettings;
}

export const platformSettingsSchema = z.object({
  low_stock_enabled: z.boolean().default(true),
  low_stock_threshold: z.number().int().positive().default(10),
  chargeback_enabled: z.boolean().default(true),
  order_notifications_enabled: z.boolean().default(false).optional(),
  order_notification_types: z.array(z.string()).default(['new', 'cancelled']).optional(),
  failed_payment_enabled: z.boolean().default(false).optional(),
  high_value_order_enabled: z.boolean().default(false).optional(),
  high_value_threshold: z.number().int().positive().default(3000).optional(),
  review_alerts_enabled: z.boolean().default(false).optional(),
  min_review_rating: z.number().int().min(1).max(5).default(3).optional(),
});

export type PlatformSettings = z.infer<typeof platformSettingsSchema>;

export interface PlatformWithSettings extends Platform {
  settings: PlatformSettings;
}
