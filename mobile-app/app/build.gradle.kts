plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.sttalis.artisan"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.sttalis.artisan"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "2.2.2"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.activity)
    implementation(libs.androidx.constraintlayout)


    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)


    implementation(libs.google.gson)
    implementation(libs.androidx.lifecycle.runtime)
    implementation(libs.androidx.lifecycle.livedata)

    implementation("androidx.navigation:navigation-fragment-ktx:2.7.7")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.7")
    implementation("androidx.drawerlayout:drawerlayout:1.2.0")

    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")

    implementation("com.google.code.gson:gson:2.10.1")

    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4")

    implementation("com.squareup.okhttp3:logging-interceptor:4.9.0")

    
}

tasks.whenTaskAdded {
    if (name.startsWith("package")) {
        doLast {
            val variantName = name.removePrefix("package")
                .replace("ForUnitTest", "")
                .replaceFirstChar { it.lowercase() }

            val versionName = android.defaultConfig.versionName
            val apkName = "Artisan-v.apk"

            val projectRoot = project.rootDir
            val buildDir = layout.buildDirectory.get().asFile

            val destinationDir = File(projectRoot, "APK/$variantName")
            val apkDir = File(buildDir, "outputs/apk/$variantName")

            if (apkDir.exists()) {
                val apkFile = apkDir.walk().find { it.name.endsWith(".apk") && !it.name.contains("unaligned") }

                if (apkFile != null) {
                    println("APK encontrado: ${apkFile.name}. Copiando para $destinationDir...")
                    copy {
                        from(apkFile)
                        into(destinationDir)
                        rename { apkName }
                    }
                    println("APK copiado e renomeado para: $destinationDir/$apkName")
                } else {
                    println("Nenhum arquivo APK válido encontrado na pasta: $apkDir")
                }
            }
        }
    }
}