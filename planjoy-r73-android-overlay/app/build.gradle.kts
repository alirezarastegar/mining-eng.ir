plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.plugin.compose")
}
android {
    namespace="com.planjoy.r7"
    compileSdk=37
    defaultConfig { applicationId="app.planjoy.local"; minSdk=26; targetSdk=37; versionCode=73000; versionName="0.7.3" }
    flavorDimensions += "install"
    productFlavors {
        create("production") { dimension = "install" }
        create("cleanTest") { dimension = "install"; applicationIdSuffix = ".clean73"; versionNameSuffix = "-clean" }
    }
    buildFeatures { compose=true }
    buildTypes { release { isMinifyEnabled=false; isShrinkResources=false; proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"),"proguard-rules.pro") } }
    lint { checkReleaseBuilds = false }
}
dependencies {
    val bom=platform("androidx.compose:compose-bom:2026.08.00")
    implementation(bom)
    androidTestImplementation(bom)
    implementation("androidx.activity:activity-compose:1.13.0")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    debugImplementation("androidx.compose.ui:ui-tooling")
}
