package com.aiadviser.startup;

import com.aiadviser.service.DataSyncService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class StartupDataSyncRunner implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(StartupDataSyncRunner.class);

    private final DataSyncService dataSyncService;

    public StartupDataSyncRunner(DataSyncService dataSyncService) {
        this.dataSyncService = dataSyncService;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        log.info("=== Starting automatic product synchronization on application startup ===");
        
        try {
            dataSyncService.syncProductsFromExternalSources();
            log.info("=== Startup product synchronization completed successfully ===");
        } catch (Exception e) {
            log.error("=== Startup product synchronization failed: {} ===", e.getMessage(), e);
        }
    }
}
