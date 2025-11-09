import { type Platform, type InsertPlatform, type PlatformWithSettings, type PlatformSettings, type PlatformPublic } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  getPlatforms(): Promise<PlatformWithSettings[]>;
  getPlatformsPublic(): Promise<(Omit<PlatformWithSettings, 'credentials'> & { hasCredentials: boolean })[]>;
  getPlatform(id: string): Promise<PlatformWithSettings | undefined>;
  createPlatform(platform: InsertPlatform): Promise<PlatformWithSettings>;
  updatePlatformSettings(id: string, settings: PlatformSettings): Promise<PlatformWithSettings | undefined>;
  deletePlatform(id: string): Promise<boolean>;
}

export class MemStorage implements IStorage {
  private platforms: Map<string, PlatformWithSettings>;

  constructor() {
    this.platforms = new Map();
  }

  async getPlatforms(): Promise<PlatformWithSettings[]> {
    return Array.from(this.platforms.values());
  }

  async getPlatformsPublic(): Promise<(Omit<PlatformWithSettings, 'credentials'> & { hasCredentials: boolean })[]> {
    return Array.from(this.platforms.values()).map(({ credentials, ...platform }) => ({
      ...platform,
      hasCredentials: !!credentials,
    }));
  }

  async getPlatform(id: string): Promise<PlatformWithSettings | undefined> {
    return this.platforms.get(id);
  }

  async createPlatform(insertPlatform: InsertPlatform): Promise<PlatformWithSettings> {
    const id = randomUUID();
    const platform: PlatformWithSettings = {
      ...insertPlatform,
      id,
      settings: {
        low_stock_enabled: true,
        low_stock_threshold: 10,
        chargeback_enabled: true,
      },
    };
    this.platforms.set(id, platform);
    return platform;
  }

  async updatePlatformSettings(id: string, settings: PlatformSettings): Promise<PlatformWithSettings | undefined> {
    const platform = this.platforms.get(id);
    if (!platform) return undefined;
    
    platform.settings = settings;
    this.platforms.set(id, platform);
    return platform;
  }

  async deletePlatform(id: string): Promise<boolean> {
    return this.platforms.delete(id);
  }
}

export const storage = new MemStorage();
