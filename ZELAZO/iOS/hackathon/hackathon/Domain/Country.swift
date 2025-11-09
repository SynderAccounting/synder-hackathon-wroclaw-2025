//
//  Country.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//


import Foundation

struct Country: Hashable, Identifiable {
    var id = UUID().uuidString
    var flag: String
    var name: String
}

extension Country {
    static var allCountries: [Country] {
        var countries = [Country]()
        for code in NSLocale.isoCountryCodes {
            let id = NSLocale.localeIdentifier(fromComponents: [NSLocale.Key.countryCode.rawValue: code])
            let name = NSLocale(localeIdentifier: Locale.current.identifier).displayName(forKey: NSLocale.Key.identifier, value: id) ?? ""
            
            let base: UInt32 = 127397
            var flag = ""
            for scalar in code.unicodeScalars {
                if let unicode = UnicodeScalar(base + scalar.value) {
                    flag.append(String(unicode))
                }
            }
            
            countries.append(Country(flag: flag, name: name))
        }
        
        return countries.sorted(by: { $0.name < $1.name })
    }
}